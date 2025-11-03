export const timelineRange = {
  start: {
    year: 2024,
    month: 11,
  },
  end: {
    year: 2025,
    month: 5,
  },
}

export const rows = [
  {
    site: 'SSIR',
    iface: 'NVMe',
    product: 'BM9C1a',
    ctrl: 'PiccoloQ (EVT0)',
    nand: 'V7Q',
    events: [
      { id: 'e1', date: '2024-12-15', customer: 'DELL', type: 'eval', note: 'EVT sample' },
      { id: 'e2', date: '2025-01-20', customer: 'HP', type: 'plan' },
    ],
  },
  {
    site: 'SSIR',
    iface: 'NVMe',
    product: '990QVO',
    ctrl: 'PiccoloQ',
    nand: 'V9Q',
    events: [
      { id: 'e3', date: '2025-02-10', customer: 'Lenovo', type: 'issue', note: 'FW regression' },
    ],
  },
  {
    site: 'SSIR',
    iface: 'NVMe',
    product: '990PRO',
    ctrl: 'Pascal (EVT2)',
    nand: 'V8',
    events: [{ id: 'e4', date: '2025-03-05', customer: 'Acer', type: 'ship' }],
  },
  {
    site: 'SSIR',
    iface: 'NVMe',
    product: 'PM9F1',
    ctrl: 'Pascal (EVT2)',
    nand: 'V7',
    events: [{ id: 'e5', date: '2025-04-18', customer: 'DELL', type: 'risk' }],
  },
]
