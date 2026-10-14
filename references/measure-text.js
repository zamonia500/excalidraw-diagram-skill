const { createCanvas } = require('canvas');
function measureText(text, fontSize, fontFamily) {
  const cv = createCanvas(1, 1);
  const ctx = cv.getContext('2d');
  ctx.font = `${fontSize}px ${fontFamily}`;
  const lines = text.split('\n');
  const w = Math.max(...lines.map(l => ctx.measureText(l).width));
  return { width: Math.ceil(w) + 40, height: lines.length * Math.ceil(fontSize * 1.35) + 24 };
}
process.stdout.write(JSON.stringify(
  measureText(process.argv[2], parseInt(process.argv[3]), process.argv[4] || 'Virgil')
));
