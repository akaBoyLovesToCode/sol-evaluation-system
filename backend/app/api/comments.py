"""Comments API endpoints for Solution Evaluation System

This module handles comment-related API endpoints including creation,
retrieval, editing, deletion, and mention processing.
"""

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required

from app import db
from app.models.comment import Comment
from app.models.evaluation import Evaluation
from app.models.mention import Mention
from app.models.user import User
from app.utils.decorators import handle_exceptions, validate_json
from app.utils.helpers import get_current_user_id

# Create blueprint
comments_bp = Blueprint("comments", __name__)


@comments_bp.route("/evaluations/<int:evaluation_id>/comments", methods=["GET"])
@jwt_required()
@handle_exceptions
def get_evaluation_comments(evaluation_id: int):
    """Get comments for a specific evaluation

    Args:
        evaluation_id: ID of the evaluation

    Query Parameters:
        page (int): Page number for pagination
        per_page (int): Items per page
        include_replies (bool): Whether to include nested replies

    Returns:
        JSON response with comments list
    """
    try:
        # Verify evaluation exists
        evaluation = Evaluation.query.get(evaluation_id)
        if not evaluation:
            return jsonify({"error": "Evaluation not found"}), 404

        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        include_replies = request.args.get("include_replies", "true").lower() == "true"

        # Query root comments (no parent)
        query = Comment.query.filter_by(
            evaluation_id=evaluation_id, parent_comment_id=None, is_deleted=False
        ).order_by(Comment.created_at.desc())

        # Paginate
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        # Convert to dict
        comments = []
        for comment in paginated.items:
            comment_dict = comment.to_dict(
                include_replies=include_replies, include_user=True
            )
            comments.append(comment_dict)

        return jsonify(
            {
                "comments": comments,
                "total": paginated.total,
                "page": page,
                "per_page": per_page,
                "total_pages": paginated.pages,
            }
        ), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching comments: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@comments_bp.route("/evaluations/<int:evaluation_id>/comments", methods=["POST"])
@jwt_required()
@validate_json(["content"])
@handle_exceptions
def create_comment(evaluation_id: int):
    """Create a new comment on an evaluation

    Args:
        evaluation_id: ID of the evaluation

    JSON Body:
        content (str): Comment content
        mentioned_usernames (list): Optional list of mentioned usernames
        parent_comment_id (int): Optional parent comment for replies

    Returns:
        JSON response with created comment
    """
    try:
        # Verify evaluation exists
        evaluation = Evaluation.query.get(evaluation_id)
        if not evaluation:
            return jsonify({"error": "Evaluation not found"}), 404

        # Get current user
        current_user_id = get_current_user_id()

        # Get request data
        data = request.get_json()
        content = data["content"]
        mentioned_usernames = data.get("mentioned_usernames", [])
        parent_comment_id = data.get("parent_comment_id")

        # Validate parent comment if provided
        if parent_comment_id:
            parent = Comment.query.get(parent_comment_id)
            if not parent or parent.evaluation_id != evaluation_id:
                return jsonify({"error": "Invalid parent comment"}), 400
            if parent.is_deleted:
                return jsonify({"error": "Cannot reply to deleted comment"}), 400

        # Create comment with mentions
        comment = Comment.create_with_mentions(
            evaluation_id=evaluation_id,
            user_id=current_user_id,
            content=content,
            mentioned_usernames=mentioned_usernames,
            parent_comment_id=parent_comment_id,
        )

        # Send notifications for mentions
        if mentioned_usernames:
            from app.models.message import Message

            for username in mentioned_usernames:
                user = User.query.filter_by(username=username).first()
                if user and user.id != current_user_id:
                    # Create mention record
                    mention = Mention(
                        mention_type="evaluation_comment",
                        mentioned_user_id=user.id,
                        mentioner_id=current_user_id,
                        evaluation_id=evaluation_id,
                        comment_id=comment.id,
                        context_text=content,
                    )
                    db.session.add(mention)

                    # Create notification
                    Message.create_mention_notification(mention)

        db.session.commit()

        # Log the action
        from app.models.operation_log import OperationLog

        OperationLog.log_operation(
            user_id=current_user_id,
            operation_type="comment",
            target_type="evaluation",
            target_id=evaluation_id,
            details={"comment_id": comment.id, "action": "created"},
        )

        return jsonify(
            {
                "message": "Comment created successfully",
                "comment": comment.to_dict(include_user=True),
            }
        ), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating comment: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@comments_bp.route("/comments/<int:comment_id>", methods=["PUT"])
@jwt_required()
@validate_json(["content"])
@handle_exceptions
def edit_comment(comment_id: int):
    """Edit an existing comment

    Args:
        comment_id: ID of the comment

    JSON Body:
        content (str): New comment content

    Returns:
        JSON response with updated comment
    """
    try:
        # Get comment
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({"error": "Comment not found"}), 404

        # Check ownership
        current_user_id = get_current_user_id()
        if comment.user_id != current_user_id:
            return jsonify({"error": "You can only edit your own comments"}), 403

        # Check if deleted
        if comment.is_deleted:
            return jsonify({"error": "Cannot edit deleted comment"}), 400

        # Get new content
        data = request.get_json()
        new_content = data["content"]

        # Edit comment
        comment.edit(new_content)

        # Process new mentions
        mentioned_usernames = data.get("mentioned_usernames", [])
        if mentioned_usernames:
            # Clear old mentions for this comment
            Mention.query.filter_by(comment_id=comment_id).delete()

            # Create new mentions
            for username in mentioned_usernames:
                user = User.query.filter_by(username=username).first()
                if user and user.id != current_user_id:
                    mention = Mention(
                        mention_type="evaluation_comment",
                        mentioned_user_id=user.id,
                        mentioner_id=current_user_id,
                        evaluation_id=comment.evaluation_id,
                        comment_id=comment.id,
                        context_text=new_content,
                    )
                    db.session.add(mention)

        db.session.commit()

        return jsonify(
            {
                "message": "Comment updated successfully",
                "comment": comment.to_dict(include_user=True),
            }
        ), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error editing comment: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@comments_bp.route("/comments/<int:comment_id>", methods=["DELETE"])
@jwt_required()
@handle_exceptions
def delete_comment(comment_id: int):
    """Delete a comment (soft delete)

    Args:
        comment_id: ID of the comment

    Returns:
        JSON response confirming deletion
    """
    try:
        # Get comment
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({"error": "Comment not found"}), 404

        # Check ownership or admin
        current_user_id = get_current_user_id()
        current_user = User.query.get(current_user_id)

        if comment.user_id != current_user_id and current_user.role != "admin":
            return jsonify({"error": "You can only delete your own comments"}), 403

        # Check if already deleted
        if comment.is_deleted:
            return jsonify({"error": "Comment already deleted"}), 400

        # Soft delete
        comment.soft_delete()

        # Log the action
        from app.models.operation_log import OperationLog

        OperationLog.log_operation(
            user_id=current_user_id,
            operation_type="delete",
            target_type="comment",
            target_id=comment_id,
            details={"evaluation_id": comment.evaluation_id},
        )

        return jsonify({"message": "Comment deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting comment: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@comments_bp.route("/comments/<int:comment_id>/replies", methods=["GET"])
@jwt_required()
@handle_exceptions
def get_comment_replies(comment_id: int):
    """Get replies for a specific comment

    Args:
        comment_id: ID of the parent comment

    Returns:
        JSON response with replies list
    """
    try:
        # Get parent comment
        parent = Comment.query.get(comment_id)
        if not parent:
            return jsonify({"error": "Comment not found"}), 404

        # Get replies
        replies = (
            parent.replies.filter_by(is_deleted=False)
            .order_by(Comment.created_at.asc())
            .all()
        )

        # Convert to dict
        reply_list = [reply.to_dict(include_user=True) for reply in replies]

        return jsonify({"replies": reply_list, "total": len(reply_list)}), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching replies: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@comments_bp.route("/comments/<int:comment_id>/tree", methods=["GET"])
@jwt_required()
@handle_exceptions
def get_comment_tree(comment_id: int):
    """Get complete reply tree for a comment

    Args:
        comment_id: ID of the root comment

    Query Parameters:
        max_depth (int): Maximum nesting depth (default: 5)

    Returns:
        JSON response with nested reply tree
    """
    try:
        # Get comment
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({"error": "Comment not found"}), 404

        # Get max depth
        max_depth = request.args.get("max_depth", 5, type=int)

        # Get reply tree
        tree = comment.get_reply_tree(max_depth=max_depth)

        return jsonify(
            {
                "comment": comment.to_dict(include_user=True),
                "reply_tree": tree,
                "total_replies": comment.all_replies_count,
            }
        ), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching comment tree: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@comments_bp.route("/users/<int:user_id>/comments", methods=["GET"])
@jwt_required()
@handle_exceptions
def get_user_comments(user_id: int):
    """Get all comments by a specific user

    Args:
        user_id: ID of the user

    Query Parameters:
        page (int): Page number
        per_page (int): Items per page

    Returns:
        JSON response with user's comments
    """
    try:
        # Verify user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        # Query user's comments
        query = Comment.query.filter_by(user_id=user_id, is_deleted=False).order_by(
            Comment.created_at.desc()
        )

        # Paginate
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        # Convert to dict
        comments = []
        for comment in paginated.items:
            comment_dict = comment.to_dict(include_user=False)
            # Add evaluation info
            comment_dict["evaluation_number"] = comment.evaluation.evaluation_number
            comment_dict["evaluation_product"] = comment.evaluation.product_name
            comments.append(comment_dict)

        return jsonify(
            {
                "comments": comments,
                "total": paginated.total,
                "page": page,
                "per_page": per_page,
                "total_pages": paginated.pages,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                },
            }
        ), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching user comments: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
