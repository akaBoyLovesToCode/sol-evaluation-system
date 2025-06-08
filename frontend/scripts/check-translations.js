#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 读取翻译文件
const zhTranslations = JSON.parse(fs.readFileSync(path.join(__dirname, '../src/locales/zh.json'), 'utf8'));
const enTranslations = JSON.parse(fs.readFileSync(path.join(__dirname, '../src/locales/en.json'), 'utf8'));
const koTranslations = JSON.parse(fs.readFileSync(path.join(__dirname, '../src/locales/ko.json'), 'utf8'));

// 递归获取所有键
function getAllKeys(obj, prefix = '') {
  let keys = [];
  for (const key in obj) {
    const fullKey = prefix ? `${prefix}.${key}` : key;
    if (typeof obj[key] === 'object' && obj[key] !== null) {
      keys = keys.concat(getAllKeys(obj[key], fullKey));
    } else {
      keys.push(fullKey);
    }
  }
  return keys;
}

// 检查键是否存在
function hasKey(obj, keyPath) {
  const keys = keyPath.split('.');
  let current = obj;
  for (const key of keys) {
    if (current[key] === undefined) {
      return false;
    }
    current = current[key];
  }
  return true;
}

console.log('🔍 检查翻译文件完整性...\n');

// 获取所有键（以中文为基准）
const allKeys = getAllKeys(zhTranslations);

console.log(`📊 总共有 ${allKeys.length} 个翻译键\n`);

// 检查英文翻译
console.log('🇺🇸 检查英文翻译:');
const missingEnKeys = allKeys.filter(key => !hasKey(enTranslations, key));
if (missingEnKeys.length === 0) {
  console.log('✅ 英文翻译完整');
} else {
  console.log(`❌ 缺少 ${missingEnKeys.length} 个键:`);
  missingEnKeys.forEach(key => console.log(`   - ${key}`));
}

// 检查韩文翻译
console.log('\n🇰🇷 检查韩文翻译:');
const missingKoKeys = allKeys.filter(key => !hasKey(koTranslations, key));
if (missingKoKeys.length === 0) {
  console.log('✅ 韩文翻译完整');
} else {
  console.log(`❌ 缺少 ${missingKoKeys.length} 个键:`);
  missingKoKeys.forEach(key => console.log(`   - ${key}`));
}

console.log('\n🎉 翻译检查完成!');

if (missingEnKeys.length === 0 && missingKoKeys.length === 0) {
  console.log('✅ 所有翻译文件都是完整的!');
  process.exit(0);
} else {
  console.log('❌ 发现缺失的翻译键，请补充完整');
  process.exit(1);
} 