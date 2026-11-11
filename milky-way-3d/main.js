import * as THREE from 'three';
import { OrbitControls } from './lib/jsm/controls/OrbitControls.js';
import { EffectComposer } from './lib/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from './lib/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from './lib/jsm/postprocessing/UnrealBloomPass.js';
import { OutputPass } from './lib/jsm/postprocessing/OutputPass.js';

/* ============================================================
   真实银河系三维模拟
   —— 棒旋星系 SBbc：中央棒 + 四条对数螺旋主臂 + 猎户支臂
   半径标定：100 单位 ≈ 5 万光年，太阳位于半径 26 处
   ============================================================ */

const R      = 100;                          // 银盘半径
const R0     = 12.5;                         // 旋臂起始半径（棒末端）
const B      = Math.tan(12 * Math.PI / 180); // 对数螺旋螺距角 12°
const MAX_T  = Math.log(R / R0) / B;         // 旋臂总缠绕角（约 1.55 圈）
const SUN_R  = 26;                           // 太阳到银心距离（约 2.6 万光年）
const BAR_A  = 0.44;                         // 中央棒方位角

const PHASE = {                              // 各主臂方位偏移
  scutum: 0,                    // 盾牌-半人马臂（主）
  perseus: Math.PI,             // 英仙臂（主）
  sagittarius: Math.PI / 2 + 0.35,   // 人马臂
  norma: 3 * Math.PI / 2 + 0.35,     // 矩尺臂
};

/* ---------------- 随机工具 ---------------- */
const TAU = Math.PI * 2;
const rand = (a = 1, b) => b === undefined ? Math.random() * a : a + Math.random() * (b - a);
function gauss() {
  let u = 0, v = 0;
  while (!u) u = Math.random();
  while (!v) v = Math.random();
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(TAU * v);
}
const pick = arr => arr[(Math.random() * arr.length) | 0];

/* ---------------- 星系结构采样 ---------------- */
// 对数螺旋旋臂上的一个点（宽度随半径增大）
function armPoint(phase, tight = 1) {
  const t = Math.pow(Math.random(), 0.85) * MAX_T;
  let r = R0 * Math.exp(B * t);
  const w = (1.1 + r * 0.06) * tight;
  r += gauss() * w * 0.45;
  const ang = phase + t + gauss() * w * 0.7 / Math.max(r, 4);
  const zSig = 0.55 + Math.pow(Math.min(r, R) / R, 2) * 1.5;
  return { x: Math.cos(ang) * r, y: gauss() * zSig, z: Math.sin(ang) * r, r: Math.abs(r) };
}
// 旋臂之间的银盘背景恒星（径向指数分布）
function diskPoint() {
  let r;
  do { r = -34 * Math.log(1 - Math.random()); } while (r > R);
  const ang = Math.random() * TAU;
  const zSig = 0.8 + Math.pow(r / R, 2) * 1.7;
  return { x: Math.cos(ang) * r, y: gauss() * zSig, z: Math.sin(ang) * r, r };
}
// 中央棒 + 核球（老年恒星）
function bulgePoint() {
  let x, y, z;
  if (Math.random() < 0.62) { x = gauss() * 10.5; y = gauss() * 2.9; z = gauss() * 2.8; } // 棒
  else                      { x = gauss() * 4.8; y = gauss() * 3.4; z = gauss() * 3.0; } // 核球
  const c = Math.cos(BAR_A), s = Math.sin(BAR_A);
  return { x: x * c - z * s, y: y * 0.85, z: x * s + z * c, r: Math.hypot(x, z) };
}
// 恒星晕（老年贫金属星，扁球分布）
function haloPoint() {
  const r = 14 + Math.pow(Math.random(), 1.7) * 95;
  const th = Math.acos(2 * Math.random() - 1), ph = Math.random() * TAU;
  return { x: r * Math.sin(th) * Math.cos(ph), y: r * Math.cos(th) * 0.7, z: r * Math.sin(th) * Math.sin(ph), r };
}
// 猎户支臂：位于人马臂与英仙臂之间的一段短臂，太阳在其中
const SUN_ANG = (Math.log(SUN_R / R0) / B + PHASE.perseus + Math.log(SUN_R / R0) / B + PHASE.sagittarius) / 2;
function spurPoint() {
  const t = gauss() * 0.42;
  const ang = SUN_ANG + t;
  const r = SUN_R * Math.exp(B * t) * (1 + gauss() * 0.045);
  return { x: Math.cos(ang) * r, y: gauss() * 0.5, z: Math.sin(ang) * r, r };
}

/* ---------------- 恒星光谱配色（近似黑体） ---------------- */
//          O          B          A          F          G          K          M
const SPECTRA = [
  [0.61, 0.69, 1.00], [0.66, 0.75, 1.00], [0.78, 0.84, 1.00], [0.95, 0.96, 1.00],
  [1.00, 0.95, 0.88], [1.00, 0.83, 0.63], [1.00, 0.71, 0.46],
];
// 各区域的光谱权重分布：旋臂偏蓝（年轻星），核球/晕偏橙红（老年星）
const WEIGHTS = {
  arm:   [0.06, 0.14, 0.17, 0.15, 0.15, 0.17, 0.16],
  disk:  [0.008, 0.03,  0.07, 0.12, 0.17, 0.25, 0.352],
  bulge: [0.001, 0.004, 0.02, 0.05, 0.12, 0.28, 0.525],
  halo:  [0.001, 0.004, 0.015, 0.04, 0.10, 0.26, 0.58],
};
function starColor(region) {
  const w = WEIGHTS[region];
  let x = Math.random(), i = 0;
  for (; i < w.length - 1 && (x -= w[i]) > 0; i++);
  const c = SPECTRA[i];
  const b = 0.78 + Math.random() * 0.38; // 亮度扰动
  return [c[0] * b, c[1] * b, c[2] * b];
}

/* ============================================================
   渲染器 / 场景
   ============================================================ */
let renderer;
try {
  renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('scene'), antialias: false, powerPreference: 'high-performance' });
} catch (e) {
  document.getElementById('nogl').hidden = false;
  document.getElementById('loading').classList.add('hide');
  throw e;
}
renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
renderer.setSize(innerWidth, innerHeight);
renderer.setClearColor(0x000005, 1);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.78;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(55, innerWidth / innerHeight, 0.1, 4000);
const CAM_FROM = new THREE.Vector3(-40, 240, 560);
const CAM_TO   = new THREE.Vector3(38, 62, 158);
camera.position.copy(CAM_FROM);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.minDistance = 6;
controls.maxDistance = 900;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.22;
controls.panSpeed = 0.6;
controls.enabled = false; // 开场动画期间禁用
try { controls.saveState(); } catch (e) { }

/* ---------------- 后期：Unreal Bloom ---------------- */
const composer = new EffectComposer(renderer);
composer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(innerWidth, innerHeight), 0.40, 0.50, 0.34);
composer.addPass(bloom);
composer.addPass(new OutputPass());

/* ============================================================
   程序化贴图
   ============================================================ */
function canvasTexture(size, draw) {
  const c = document.createElement('canvas');
  c.width = c.height = size;
  draw(c.getContext('2d'), size);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
// 柔光斑（渐变半径只占纹理 42%，边缘完全透明，杜绝 Bloom 后的方形轮廓）
const texGlow = (inner = 'rgba(255,255,255,1)', mid = 'rgba(255,255,255,0.28)') =>
  canvasTexture(256, (g, s) => {
    const c = s / 2, r = s * 0.42;
    const grd = g.createRadialGradient(c, c, 0, c, c, r);
    grd.addColorStop(0, inner); grd.addColorStop(0.18, mid); grd.addColorStop(0.38, 'rgba(0,0,0,0.16)');
    grd.addColorStop(0.6, 'rgba(0,0,0,0.05)'); grd.addColorStop(0.82, 'rgba(0,0,0,0.012)'); grd.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = grd; g.fillRect(0, 0, s, s);
  });
// 带衍射星芒的亮星
const texSpike = canvasTexture(256, (g, s) => {
  const c = s / 2;
  g.globalCompositeOperation = 'lighter';
  const grd = g.createRadialGradient(c, c, 0, c, c, c * 0.5);
  grd.addColorStop(0, 'rgba(255,255,255,1)'); grd.addColorStop(0.25, 'rgba(255,255,255,0.32)'); grd.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = grd; g.fillRect(0, 0, s, s);
  const spike = (len, wid, rot) => {
    g.save(); g.translate(c, c); g.rotate(rot);
    const lg = g.createLinearGradient(-len, 0, len, 0);
    lg.addColorStop(0, 'rgba(255,255,255,0)'); lg.addColorStop(0.5, 'rgba(255,255,255,0.85)'); lg.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = lg; g.fillRect(-len, -wid, len * 2, wid * 2); g.restore();
  };
  spike(c * 0.95, 1.7, 0); spike(c * 0.95, 1.7, Math.PI / 2);
  spike(c * 0.42, 1.1, Math.PI / 4); spike(c * 0.42, 1.1, 3 * Math.PI / 4);
});
// 扩散圆环（太阳系标记）
const texRing = canvasTexture(128, (g, s) => {
  g.strokeStyle = 'rgba(255,235,190,0.9)'; g.lineWidth = 2.4;
  g.shadowColor = 'rgba(255,220,150,0.9)'; g.shadowBlur = 7;
  g.beginPath(); g.arc(s / 2, s / 2, s / 2 - 9, 0, TAU); g.stroke();
});
// 黑洞事件视界（不透明黑盘，边缘柔和过渡）
const texHole = canvasTexture(256, (g, s) => {
  const c = s / 2;
  const grd = g.createRadialGradient(c, c, 0, c, c, c * 0.90);
  grd.addColorStop(0, 'rgba(0,0,0,1)');
  grd.addColorStop(0.94, 'rgba(0,0,0,1)');
  grd.addColorStop(0.975, 'rgba(0,0,0,0.5)');
  grd.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = grd; g.beginPath(); g.arc(c, c, c * 0.90, 0, TAU); g.fill();
});
// 吸积盘（细亮环）
const texDisk = canvasTexture(256, (g, s) => {
  const c = s / 2;
  const grd = g.createRadialGradient(c, c, 0, c, c, c * 0.5);
  grd.addColorStop(0.00, 'rgba(255,255,255,0)');
  grd.addColorStop(0.44, 'rgba(255,245,225,0)');
  grd.addColorStop(0.54, 'rgba(255,240,210,0.95)');
  grd.addColorStop(0.62, 'rgba(255,190,120,0.62)');
  grd.addColorStop(0.74, 'rgba(255,140,70,0.16)');
  grd.addColorStop(1.00, 'rgba(255,120,50,0)');
  g.fillStyle = grd; g.fillRect(0, 0, s, s);
});// 星云（分层光斑云絮）
function texNebula(hue, sat = 78) {
  return canvasTexture(256, (g, s) => {
    g.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 30; i++) {
      const x = s / 2 + gauss() * 30, y = s / 2 + gauss() * 30, r = 18 + Math.random() * 52;
      const grd = g.createRadialGradient(x, y, 0, x, y, r);
      grd.addColorStop(0, `hsla(${hue + rand(-22, 22)},${sat}%,${rand(42, 62)}%,${rand(0.05, 0.13)})`);
      grd.addColorStop(1, 'hsla(0,0%,0%,0)');
      g.fillStyle = grd; g.beginPath(); g.arc(x, y, r, 0, TAU); g.fill();
    }
  });
}
// 远景星系
function texFarGalaxy(tint) {
  return canvasTexture(128, (g, s) => {
    const c = s / 2;
    g.translate(c, c); g.rotate(rand(0, TAU)); g.scale(1, 0.3 + Math.random() * 0.45);
    const grd = g.createRadialGradient(0, 0, 0, 0, 0, c * 0.92);
    grd.addColorStop(0, 'rgba(255,250,238,0.95)'); grd.addColorStop(0.22, tint + '99');
    grd.addColorStop(0.6, tint + '2a'); grd.addColorStop(1, tint + '00');
    g.fillStyle = grd; g.beginPath(); g.arc(0, 0, c * 0.92, 0, TAU); g.fill();
  });
}

/* ============================================================
   着色器
   ============================================================ */
const starVert = /* glsl */`
  uniform float uPx; uniform float uTime; uniform float uScale;
  attribute float aSize; attribute float aPhase; attribute vec3 aColor;
  varying vec3 vColor; varying float vTw;
  void main(){
    vColor = aColor;
    vTw = 0.82 + 0.18 * sin(uTime * (0.5 + fract(aPhase) * 1.9) + aPhase * 23.0);
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    gl_PointSize = clamp(aSize * uScale * uPx / max(-mv.z, 0.1), 0.75, 90.0);
    gl_Position = projectionMatrix * mv;
  }`;
const starFrag = /* glsl */`
  uniform float uOpacity;
  varying vec3 vColor; varying float vTw;
  void main(){
    float d = length(gl_PointCoord - 0.5);
    if (d > 0.5) discard;
    float glow = pow(smoothstep(0.5, 0.0, d), 2.6);
    float core = smoothstep(0.17, 0.0, d);
    float a = (glow * 0.85 + core) * vTw * uOpacity;
    if (a < 0.004) discard;
    gl_FragColor = vec4(vColor * (0.75 + core * 1.6), a);
  }`;
const hazeFrag = /* glsl */`
  uniform float uOpacity;
  varying vec3 vColor; varying float vTw;
  void main(){
    float d = length(gl_PointCoord - 0.5);
    if (d > 0.5) discard;
    float a = pow(smoothstep(0.5, 0.0, d), 3.1) * vTw * uOpacity;
    if (a < 0.003) discard;
    gl_FragColor = vec4(vColor, a);
  }`;
const dustFrag = /* glsl */`
  uniform float uOpacity;
  varying vec3 vColor; varying float vTw;
  void main(){
    float d = length(gl_PointCoord - 0.5);
    if (d > 0.5) discard;
    float a = smoothstep(0.5, 0.06, d) * uOpacity;
    if (a < 0.004) discard;
    gl_FragColor = vec4(vColor, a);
  }`;
const texStarVert = /* glsl */`
  uniform float uPx; uniform float uTime;
  attribute float aSize; attribute float aPhase; attribute vec3 aColor;
  varying vec3 vColor; varying float vTw;
  void main(){
    vColor = aColor;
    vTw = 0.86 + 0.14 * sin(uTime * (0.4 + fract(aPhase) * 1.4) + aPhase * 31.0);
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    gl_PointSize = clamp(aSize * uPx / max(-mv.z, 0.1), 1.0, 160.0);
    gl_Position = projectionMatrix * mv;
  }`;
const texStarFrag = /* glsl */`
  uniform sampler2D uMap; uniform float uOpacity;
  varying vec3 vColor; varying float vTw;
  void main(){
    vec4 tx = texture2D(uMap, gl_PointCoord);
    float a = tx.a * vTw * uOpacity;
    if (a < 0.004) discard;
    gl_FragColor = vec4(vColor * tx.rgb * 1.6, a);
  }`;
const bgVert = /* glsl */`
  uniform float uTime;
  attribute float aSize; attribute float aPhase; attribute vec3 aColor;
  varying vec3 vColor; varying float vTw;
  void main(){
    vColor = aColor;
    vTw = 0.78 + 0.22 * sin(uTime * (0.4 + fract(aPhase) * 2.2) + aPhase * 29.0);
    gl_PointSize = aSize;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }`;

function makePointsMaterial({ frag, px = true, opacity = 1, blending = THREE.AdditiveBlending, extraUniforms = {} }) {
  return new THREE.ShaderMaterial({
    uniforms: {
      uPx: { value: px ? pxValue() : 1 },
      uTime: { value: 0 },
      uScale: { value: 1 },
      uOpacity: { value: opacity },
      ...extraUniforms,
    },
    vertexShader: px ? starVert : bgVert,
    fragmentShader: frag,
    transparent: true,
    depthWrite: false,
    depthTest: true,
    blending,
  });
}
function pxValue() {
  return (renderer.domElement.height / renderer.getPixelRatio()) * 0.5 / Math.tan(THREE.MathUtils.degToRad(camera.fov * 0.5));
}

/* ============================================================
   粒子缓冲构建
   ============================================================ */
function buildBuffer(count, sampler, colorRegion, sizeFn, dim = 1) {
  const pos = new Float32Array(count * 3), col = new Float32Array(count * 3);
  const size = new Float32Array(count), phase = new Float32Array(count);
  for (let i = 0; i < count; i++) {
    const p = sampler(), c = starColor(colorRegion);
    pos[i * 3] = p.x; pos[i * 3 + 1] = p.y; pos[i * 3 + 2] = p.z;
    col[i * 3] = c[0] * dim; col[i * 3 + 1] = c[1] * dim; col[i * 3 + 2] = c[2] * dim;
    size[i] = sizeFn(p);
    phase[i] = Math.random() * 100;
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setAttribute('aColor', new THREE.BufferAttribute(col, 3));
  g.setAttribute('aSize', new THREE.BufferAttribute(size, 1));
  g.setAttribute('aPhase', new THREE.BufferAttribute(phase, 1));
  return g;
}

// 真空带：把范围内侧的点全部隐藏，形成黑洞与星云之间的真空
function clearInner(points, minR) {
  const g = points.geometry;
  const pos = g.getAttribute('position'), size = g.getAttribute('aSize'), col = g.getAttribute('aColor');
  if (!size) return;
  for (let i = 0; i < pos.count; i++) {
    if (Math.hypot(pos.getX(i), pos.getZ(i)) < minR) {
      size.setX(i, 0);
      if (col) col.setXYZ(i, 0, 0, 0);
    }
  }
  size.needsUpdate = true;
  if (col) col.needsUpdate = true;
}
const galaxy = new THREE.Group();
scene.add(galaxy);

/* ---------- 主星场：约 15.6 万颗 ---------- */
const N_ARM = 80000, N_DISK = 26000, N_BULGE = 44000, N_HALO = 6000;
const starGeo = new THREE.BufferGeometry();
{
  const total = N_ARM + N_DISK + N_BULGE + N_HALO;
  const pos = new Float32Array(total * 3), col = new Float32Array(total * 3);
  const size = new Float32Array(total), phase = new Float32Array(total);
  let i = 0;
  const put = p => {
    const c = starColor(p.region);
    pos[i * 3] = p.x; pos[i * 3 + 1] = p.y; pos[i * 3 + 2] = p.z;
    col[i * 3] = c[0]; col[i * 3 + 1] = c[1]; col[i * 3 + 2] = c[2];
    size[i] = p.s; phase[i] = Math.random() * 100; i++;
  };
  for (let k = 0; k < N_ARM; k++)   { const p = armPoint(pick([PHASE.scutum, PHASE.perseus, PHASE.sagittarius, PHASE.norma]), Math.random() < 0.5 ? 1 : 0.72); p.region = 'arm';   p.s = 0.32 + Math.pow(Math.random(), 3) * 0.85; put(p); }
  for (let k = 0; k < N_DISK; k++)  { const p = diskPoint();  p.region = 'disk';  p.s = 0.28 + Math.pow(Math.random(), 3) * 0.7;  put(p); }
  for (let k = 0; k < N_BULGE; k++) { const p = bulgePoint(); p.region = 'bulge'; p.s = 0.26 + Math.pow(Math.random(), 3) * 0.6;  put(p); }
  for (let k = 0; k < N_HALO; k++) { // 一半来自球状星团
    const p = (k % 2 === 0)
      ? (() => { const h = haloPoint(); return { x: h.x + gauss() * 0.55, y: h.y + gauss() * 0.55, z: h.z + gauss() * 0.55 }; })()
      : haloPoint();
    p.region = 'halo'; p.s = 0.22 + Math.random() * 0.4; put(p);
  }
  starGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  starGeo.setAttribute('aColor', new THREE.BufferAttribute(col, 3));
  starGeo.setAttribute('aSize', new THREE.BufferAttribute(size, 1));
  starGeo.setAttribute('aPhase', new THREE.BufferAttribute(phase, 1));
}
const TOTAL_STARS = N_ARM + N_DISK + N_BULGE + N_HALO;
const starMat = makePointsMaterial({ frag: starFrag, opacity: 0.86 });
const stars = new THREE.Points(starGeo, starMat);
stars.renderOrder = 2;
// galaxy.add(stars);   // 移除程序化恒星，只保留记忆星

/* ---------- 亮星（带星芒） ---------- */
const N_BRIGHT = 3200;
const brightMat = makePointsMaterial({ frag: texStarFrag, opacity: 0.74, extraUniforms: { uMap: { value: texSpike } } });
const bright = new THREE.Points(buildBuffer(N_BRIGHT, () => {
  const p = armPoint(pick([PHASE.scutum, PHASE.perseus, PHASE.sagittarius, PHASE.norma]));
  p.s = 1.1 + Math.pow(Math.random(), 2.2) * 1.9;
  return p;
}, 'arm', p => p.s), brightMat);
// 亮星强制蓝白色
{
  const col = bright.geometry.getAttribute('aColor');
  for (let i = 0; i < N_BRIGHT; i++) {
    const c = pick(SPECTRA.slice(0, 3)), b = 0.85 + Math.random() * 0.3;
    col.setXYZ(i, c[0] * b, c[1] * b, c[2] * b);
  }
}
bright.renderOrder = 2;
// galaxy.add(bright);  // 移除程序化亮星

/* ---------- 弥漫气体（星际介质辉光） ---------- */
const N_HAZE = 10000;
const hazeGeo = buildBuffer(N_HAZE, () => {
  const u = Math.random();
  let p;
  if (u < 0.58)      p = armPoint(pick([PHASE.scutum, PHASE.perseus, PHASE.sagittarius, PHASE.norma]), 0.75);
  else if (u < 0.78) p = bulgePoint();
  else               p = diskPoint();
  p.s = 3 + Math.pow(Math.random(), 2.2) * 8;
  return p;
}, 'disk', p => p.s, 0.3);
{ // 手工调色：核球暖黄、旋臂蓝白、HII 区粉色
  const pos = hazeGeo.getAttribute('position'), col = hazeGeo.getAttribute('aColor');
  const warm = new THREE.Color(1.0, 0.72, 0.42), cool = new THREE.Color(0.5, 0.62, 1.0), pink = new THREE.Color(1.0, 0.3, 0.5);
  for (let i = 0; i < N_HAZE; i++) {
    const x = pos.getX(i), z = pos.getZ(i), r = Math.hypot(x, z);
    let c;
    if (r < 13) c = warm;
    else if (Math.random() < 0.1) c = pink;
    else c = cool;
    const b = 0.5 + Math.random() * 0.5;
    col.setXYZ(i, c.r * b, c.g * b, c.b * b);
  }
}
const hazeMat = makePointsMaterial({ frag: hazeFrag, opacity: 0.055 });
const haze = new THREE.Points(hazeGeo, hazeMat);
haze.renderOrder = 1;
galaxy.add(haze);

/* ---------- 尘埃带（暗尘埃，法线混合遮光） ---------- */
const N_DUST = 16000;
const dustGeo = new THREE.BufferGeometry();
{
  const pos = new Float32Array(N_DUST * 3), col = new Float32Array(N_DUST * 3);
  const size = new Float32Array(N_DUST), phase = new Float32Array(N_DUST);
  for (let i = 0; i < N_DUST; i++) {
    let p;
    if (Math.random() < 0.86) {
      p = armPoint(pick([PHASE.scutum, PHASE.perseus, PHASE.sagittarius, PHASE.norma]), 0.5);
      // 向旋臂内缘偏移，形成暗尘带
      const w = (1.1 + Math.max(p.r, R0) * 0.06) * 0.5;
      const shift = gauss() * w * 0.8 / Math.max(p.r, 4);
      const ang = Math.atan2(p.z, p.x) - shift * 1.9;
      const rr = Math.hypot(p.x, p.z) * (1 + gauss() * 0.02);
      p.x = Math.cos(ang) * rr; p.z = Math.sin(ang) * rr;
      p.y = gauss() * 0.4;
    } else {
      const r = rand(10, 72), ang = Math.random() * TAU;
      p = { x: Math.cos(ang) * r, y: gauss() * 0.5, z: Math.sin(ang) * r };
    }
    pos[i * 3] = p.x; pos[i * 3 + 1] = p.y; pos[i * 3 + 2] = p.z;
    const b = 0.75 + Math.random() * 0.5;
    col[i * 3] = 0.055 * b; col[i * 3 + 1] = 0.042 * b; col[i * 3 + 2] = 0.038 * b;
    size[i] = 2 + Math.pow(Math.random(), 1.6) * 6.5;
    phase[i] = 0;
  }
  dustGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  dustGeo.setAttribute('aColor', new THREE.BufferAttribute(col, 3));
  dustGeo.setAttribute('aSize', new THREE.BufferAttribute(size, 1));
  dustGeo.setAttribute('aPhase', new THREE.BufferAttribute(phase, 1));
}
const dustMat = new THREE.ShaderMaterial({
  uniforms: { uPx: { value: pxValue() }, uTime: { value: 0 }, uScale: { value: 1 }, uOpacity: { value: 0.12 } },
  vertexShader: starVert, fragmentShader: dustFrag,
  transparent: true, depthWrite: false, blending: THREE.NormalBlending,
});
const dust = new THREE.Points(dustGeo, dustMat);
dust.renderOrder = 3;
galaxy.add(dust);

/* ---------- 星云精灵 ---------- */
const nebGroup = new THREE.Group();
const nebTexes = [texNebula(338), texNebula(222), texNebula(178), texNebula(268)];
for (let i = 0; i < 6; i++) {
  const m = new THREE.SpriteMaterial({
    map: pick(nebTexes), transparent: true, depthWrite: false,
    blending: THREE.AdditiveBlending, opacity: rand(0.045, 0.10), rotation: rand(TAU),
  });
  const sp = new THREE.Sprite(m);
  const p = armPoint(pick([PHASE.scutum, PHASE.perseus, PHASE.sagittarius, PHASE.norma]), 0.65);
  sp.position.set(p.x, p.y * 0.6, p.z);

  const s = rand(10, 26);
  sp.scale.set(s, s * rand(0.6, 1), 1);
  sp.renderOrder = 4;
  sp.userData.phase = rand(TAU);
  sp.userData.base = m.opacity;
  nebGroup.add(sp);
}
galaxy.add(nebGroup);

/* ---------- 银心辉光（还原项目原始中心） ---------- */
const coreGroup = new THREE.Group();
{
  const layers = [
    { s: 4,   o: 0.34, tex: texGlow('rgba(255,252,240,1)', 'rgba(255,236,190,0.5)') },
    { s: 11,  o: 0.20, tex: texGlow('rgba(255,240,205,0.95)', 'rgba(255,205,140,0.35)') },
    { s: 22,  o: 0.11, tex: texGlow('rgba(255,218,160,0.8)', 'rgba(255,170,100,0.22)') },
    { s: 40,  o: 0.05, tex: texGlow('rgba(255,200,140,0.6)', 'rgba(200,140,90,0.16)') },
  ];
  for (const L of layers) {
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: L.tex, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, opacity: L.o }));
    sp.scale.set(L.s, L.s, 1); sp.renderOrder = 5;
    coreGroup.add(sp);
  }
}
galaxy.add(coreGroup);



/* ---------- 银盘外围淡晕 ---------- */
{
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({
    map: texGlow('rgba(110,130,220,0.32)', 'rgba(90,110,190,0.1)'),
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, opacity: 0.14,
  }));
  sp.scale.set(215, 155, 1); sp.renderOrder = 0;
  galaxy.add(sp);
}

/* ---------- 太阳系标记 ---------- */
const sunAnchor = new THREE.Object3D();
sunAnchor.position.set(Math.cos(SUN_ANG) * SUN_R, 0.3, Math.sin(SUN_ANG) * SUN_R);
galaxy.add(sunAnchor);
const markerGroup = new THREE.Group();
{
  const glow = new THREE.Sprite(new THREE.SpriteMaterial({ map: texGlow('rgba(255,244,214,1)', 'rgba(255,220,150,0.4)'), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending }));
  glow.scale.set(2.6, 2.6, 1);
  const ring = new THREE.Sprite(new THREE.SpriteMaterial({ map: texRing, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending }));
  ring.userData.isRing = true;
  markerGroup.add(glow, ring);
}
sunAnchor.add(markerGroup);

/* ---------- 背景恒星 + 远景星系 ---------- */
const bg = new THREE.Group();
scene.add(bg);
{
  const N1 = 6500, N2 = 3200, N = N1 + N2;
  const pos = new Float32Array(N * 3), col = new Float32Array(N * 3);
  const size = new Float32Array(N), phase = new Float32Array(N);
  for (let i = 0; i < N; i++) {
    const near = i >= N1;
    const r = near ? rand(320, 700) : rand(880, 1200);
    const th = Math.acos(2 * Math.random() - 1), ph = Math.random() * TAU;
    pos[i * 3] = r * Math.sin(th) * Math.cos(ph);
    pos[i * 3 + 1] = r * Math.cos(th);
    pos[i * 3 + 2] = r * Math.sin(th) * Math.sin(ph);
    const c = pick(SPECTRA), b = near ? 0.5 : 0.42;
    col[i * 3] = c[0] * b; col[i * 3 + 1] = c[1] * b; col[i * 3 + 2] = c[2] * b;
    size[i] = near ? rand(0.9, 2.2) : rand(0.7, 1.7);
    phase[i] = Math.random() * 100;
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setAttribute('aColor', new THREE.BufferAttribute(col, 3));
  g.setAttribute('aSize', new THREE.BufferAttribute(size, 1));
  g.setAttribute('aPhase', new THREE.BufferAttribute(phase, 1));
  const bgMat = makePointsMaterial({ frag: starFrag, px: false, opacity: 0.55 });
  bgMat.vertexShader = bgVert.replace('gl_PointSize = aSize;', 'gl_PointSize = aSize * (0.85 + 0.3 * vTw);');
  const pts = new THREE.Points(g, bgMat);
  pts.renderOrder = -1;
  // bg.add(pts);  // 只保留记忆点
}
{
  const farTexes = [texFarGalaxy('#ffd9a8'), texFarGalaxy('#a8c0ff'), texFarGalaxy('#ffc0d8')];
  for (let i = 0; i < 26; i++) {
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({
      map: pick(farTexes), transparent: true, depthWrite: false,
      blending: THREE.AdditiveBlending, opacity: rand(0.10, 0.28), rotation: rand(TAU),
    }));
    const r = rand(760, 1150);
    const th = Math.acos(2 * Math.random() - 1), ph = Math.random() * TAU;
    sp.position.set(r * Math.sin(th) * Math.cos(ph), r * Math.cos(th), r * Math.sin(th) * Math.sin(ph));
    const s = rand(7, 20);
    sp.scale.set(s, s * rand(0.5, 0.95), 1);
    sp.renderOrder = -1;
    // bg.add(sp);
  }
}

/* ============================================================
   HTML 标注
   ============================================================ */
const labelRoot = document.getElementById('labels') || document.createElement('div'); if (labelRoot) labelRoot.style.display = 'none';
const labels = [];
function addLabel(text, en, cls, anchor) {
  const el = document.createElement('div');
  el.className = 'lbl ' + cls;
  el.innerHTML = text + (en ? `<small>${en}</small>` : '');
  labelRoot.appendChild(el);
  labels.push({ el, anchor });
}
function armAnchor(phase, t, dy = 2.5) {
  const r = R0 * Math.exp(B * t), a = phase + t;
  const o = new THREE.Object3D();
  o.position.set(Math.cos(a) * r, dy, Math.sin(a) * r);
  galaxy.add(o);
  return o;
}
addLabel('银心 · 人马座 A*', 'SGR A*', 'core', (() => { const o = new THREE.Object3D(); o.position.set(0, 1.5, 0); galaxy.add(o); return o; })());
addLabel('太阳系', 'SOLAR SYSTEM', 'sun', sunAnchor);
addLabel('盾牌 - 半人马臂', 'SCUTUM–CENTAURUS', '', armAnchor(PHASE.scutum, 7.6));
addLabel('英仙臂', 'PERSEUS ARM', '', armAnchor(PHASE.perseus, 8.2));
addLabel('人马臂', 'SAGITTARIUS ARM', '', armAnchor(PHASE.sagittarius, 6.6));
addLabel('矩尺臂', 'NORMA ARM', '', armAnchor(PHASE.norma, 7.2));
addLabel('猎户支臂 · 本地臂', 'ORION SPUR', '', (() => {
  const o = new THREE.Object3D();
  const a = SUN_ANG - 0.5, r = SUN_R * Math.exp(B * -0.5);
  o.position.set(Math.cos(a) * r, 2.2, Math.sin(a) * r);
  galaxy.add(o); return o;
})());

const _v = new THREE.Vector3();
function updateLabels() {
  const dist = camera.position.length();
  for (const L of labels) {
    L.anchor.getWorldPosition(_v).project(camera);
    const behind = _v.z > 1;
    const x = (_v.x * 0.5 + 0.5) * innerWidth;
    const y = (-_v.y * 0.5 + 0.5) * innerHeight;
    const vis = behind || x < -60 || x > innerWidth + 60 || y < -40 || y > innerHeight + 40 ? 0 : 1;
    L.el.style.display = vis ? '' : 'none';
    if (vis) {
      L.el.style.left = x + 'px';
      L.el.style.top = y + 'px';
      // 距离太近时淡出，避免遮挡
      L.el.style.opacity = Math.min(1, Math.max(0, (dist - 55) / 60));
    }
  }
}

/* ============================================================
   UI 交互
   ============================================================ */
const $ = id => document.getElementById(id);
let spinOn = true, timeScale = 1;
$('chkSpin').onchange = e => spinOn = e.target.checked;
$('chkCruise').onchange = e => controls.autoRotate = e.target.checked;
const _cl = document.getElementById('chkLabels'); if (_cl) _cl.onchange = e => labelRoot.style.display = e.target.checked ? '' : 'none';
const _cm = document.getElementById('chkMarker'); if (_cm) _cm.onchange = e => markerGroup.visible = e.target.checked;
$('rngBloom').oninput = e => bloom.strength = +e.target.value;
$('rngTime').oninput = e => timeScale = +e.target.value;
addEventListener('keydown', e => {
  if (e.code === 'Space') { e.preventDefault(); $('chkSpin').checked = spinOn = !spinOn; }
  else if (e.key === 'r' || e.key === 'R') { const c = $('chkCruise'); c.checked = controls.autoRotate = !c.checked; }
  else if (e.key === 'l' || e.key === 'L') { const c = chkLabels; if (c) { c.checked = !c.checked; labelRoot.style.display = c.checked ? '' : 'none'; } }
  else if (e.key === 'h' || e.key === 'H') document.body.classList.toggle('cinema');
});
/* ============================================================
   记忆星层：每一条记忆 = 一个可点击的光点
   ============================================================ */
const EMOC = {
  '开心': [1.00, 0.83, 0.40], '难过': [0.36, 0.55, 0.95], '生气': [0.95, 0.30, 0.38],
  '兴奋': [1.00, 0.62, 0.18], '无语': [0.62, 0.55, 1.00], '平静': [0.60, 0.80, 0.95],
  '担心': [0.55, 0.66, 1.00], '着急': [1.00, 0.55, 0.40],
};
let memData = [], memPoints = null, memMat = null;
const memPanel = document.getElementById('memp');
const memMeta = document.getElementById('memp-meta');
const memText = document.getElementById('memp-text');
const memRay = new THREE.Raycaster();
memRay.params.Points.threshold = 1.8;
const MEM_ARMS = [PHASE.scutum, PHASE.perseus, PHASE.sagittarius, PHASE.norma];

fetch('memory_stars.json').then(r => r.json()).then(list => {
  if (!Array.isArray(list) || !list.length) {
    $('starCount').textContent = '0 颗记忆星';
    $('loading-count').textContent = '0';
    return;
  }
  memData = list;
  const n = list.length;
  const t0 = list[0].ts, t1 = list[n - 1].ts || t0 + 1;
  const pos = new Float32Array(n * 3), col = new Float32Array(n * 3);
  const size = new Float32Array(n), phase = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    const m = list[i];
    const f = (m.ts - t0) / Math.max(1, t1 - t0);
    const p = armPoint(MEM_ARMS[i % 4], 1.02 - f * 0.88);
    pos[i * 3] = p.x + gauss() * 1.0;
    pos[i * 3 + 1] = 0.7 + gauss() * 0.8;
    pos[i * 3 + 2] = p.z + gauss() * 1.0;
    // 与原版恒星同色板、同尺寸
    const c = starColor('arm');
    const ret = (typeof m.retention === 'number') ? m.retention : 0.6;   // 艾宾浩斯保持度
    const dim = 0.45 + 0.55 * ret;
    col[i * 3] = c[0] * dim; col[i * 3 + 1] = c[1] * dim; col[i * 3 + 2] = c[2] * dim;
    size[i] = (0.32 + Math.pow(Math.random(), 3) * 0.85) * (0.55 + 0.75 * ret);
    phase[i] = Math.random() * 100;
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setAttribute('aColor', new THREE.BufferAttribute(col, 3));
  g.setAttribute('aSize', new THREE.BufferAttribute(size, 1));
  g.setAttribute('aPhase', new THREE.BufferAttribute(phase, 1));
  memMat = makePointsMaterial({ frag: starFrag, opacity: 0.86 });
  memPoints = new THREE.Points(g, memMat);
  memPoints.renderOrder = 2;
  galaxy.add(memPoints);
  window.__memPoints = memPoints;
  window.__cam = camera;
  window.__memData = memData;
  window.__memScreen = (i) => {
    const a = memPoints.geometry.getAttribute('position');
    const v = new THREE.Vector3(a.getX(i), a.getY(i), a.getZ(i));
    memPoints.localToWorld(v);
    v.project(camera);
    return [(v.x * 0.5 + 0.5) * innerWidth, (-v.y * 0.5 + 0.5) * innerHeight, v.z];
  };
  $('starCount').textContent = n + ' 颗记忆星';
  $('loading-count').textContent = n;
}).catch(e => console.warn('记忆加载失败', e));

renderer.domElement.addEventListener('click', ev => {
  if (!memPoints) return;
  const rect = renderer.domElement.getBoundingClientRect();
  const mouse = new THREE.Vector2(
    ((ev.clientX - rect.left) / rect.width) * 2 - 1,
    -((ev.clientY - rect.top) / rect.height) * 2 + 1
  );
  // 点到中心核心 → 弹出核心对话框
  {
    const cv2 = new THREE.Vector3(0, 0, 0).project(camera);
    const cxs = (cv2.x * 0.5 + 0.5) * innerWidth;
    const cys = (-cv2.y * 0.5 + 0.5) * innerHeight;
    window.__dbg = 'center-test ' + ev.clientX + ',' + ev.clientY + ' vs ' + cxs.toFixed(1) + ',' + cys.toFixed(1);
    if (Math.hypot(ev.clientX - cxs, ev.clientY - cys) < 50) {
      selectedMem = -1;
      memMeta.textContent = '安诗鱼 · 所记住的事情';
      const n = (memData && memData.length) ? memData.length : 400;
      memText.textContent = '这里是安诗鱼所记住的事情，共 ' + n + ' 件。';
      memPanel.style.display = 'block';
      return;
    }
  }
  // 先按屏幕距离找最近星（手机上点小点更准）
  {
    let near = -1, best = 30;
    for (let i = 0; i < memData.length; i++) {
      const sc = window.__memScreen(i);
      if (sc[2] > 1) continue;
      const d = Math.hypot(ev.clientX - sc[0], ev.clientY - sc[1]);
      if (d < best) { best = d; near = i; }
    }
    if (near >= 0) { window.__showMem(near); return; }
  }
  memRay.setFromCamera(mouse, camera);
  const hits = memRay.intersectObject(memPoints, false);
  if (hits.length) {
    selectedMem = hits[0].index;
    const m = memData[hits[0].index];
    memMeta.textContent = new Date(m.ts * 1000).toLocaleString('zh-CN') + ' · ' + m.emo + ' · ' + (m.role === 'memory' ? '安诗鱼所记住的事情' : '安诗鱼想说的');
    memText.textContent = m.view || m.text;
    memPanel.style.display = 'block';
  } else {
    memPanel.style.display = 'none';
    selectedMem = null;
  }
});
/* ---------- 记忆详情 / 搜索定位 ---------- */
window.__showMem = function (i) {
  if (!memData || !memData[i]) return;
  selectedMem = i;
  const m = memData[i];
  memMeta.textContent = '第 ' + (i + 1) + ' 颗星 · ' + new Date(m.ts * 1000).toLocaleString('zh-CN')
    + ' · ' + m.emo;
  memText.textContent = m.view || m.text;
  memPanel.style.display = 'block';
};

window.__focusMem = function (i) {
  if (!memData || !memData[i] || !memPoints) return;
  const a = memPoints.geometry.getAttribute('position');
  const pos = new THREE.Vector3(a.getX(i), a.getY(i), a.getZ(i));
  memPoints.localToWorld(pos);
  const dir = camera.position.clone().sub(pos);
  if (dir.lengthSq() < 1e-6) dir.set(0, 0, 1);
  dir.normalize();
  controls.target.copy(pos);
  camera.position.copy(pos.clone().add(dir.multiplyScalar(45)));
  controls.update();
  window.__showMem(i);
};

(function () {
  const input = document.getElementById('memSearchInput');
  const list = document.getElementById('memSearchList');
  if (!input || !list) return;
  function render(q) {
    const data = window.__memData || [];
    const hits = [];
    for (let i = 0; i < data.length && hits.length < 25; i++) {
      const t = (data[i].view || data[i].text || '');
      if (!q || t.indexOf(q) >= 0) hits.push({ i: i, t: t });
    }
    list.innerHTML = hits.map(h =>
      '<div data-i="' + h.i + '" style="padding:6px 4px;border-bottom:1px solid #1a2236;cursor:pointer;'
      + 'font-size:11px;line-height:1.5;color:#cfe0ff">'
      + '<span style="color:#ffd48a">第' + (h.i + 1) + '颗</span> '
      + h.t.slice(0, 32) + (h.t.length > 32 ? '…' : '') + '</div>'
    ).join('') || '<div style="color:#5f6c96;font-size:11px;padding:6px">没有找到</div>';
    list.querySelectorAll('[data-i]').forEach(el => {
      el.onclick = () => { window.__focusMem(parseInt(el.getAttribute('data-i'), 10)); };
    });
  }
  input.addEventListener('input', () => render(input.value.trim()));
  // 等记忆加载完成后初始化列表
  const timer = setInterval(() => {
    if (window.__memData && window.__memData.length) { render(''); clearInterval(timer); }
  }, 700);
  setTimeout(() => clearInterval(timer), 30000);
})();

/* ---------- 她的生活面板 ---------- */
async function refreshLife() {
  try {
    const st = await (await fetch('life/status.json?t=' + Date.now())).json();
    const el = document.getElementById('life-status');
    if (el) {
      if (st.waiting) {
        el.innerHTML = '<span style="color:#8fa2d8">她还没醒 · 等你跟她说第一句话</span>';
      } else {
        const p = st.silent ? '（在休息）' : '';
        el.innerHTML = `${st.location} · ${st.activity}${p}` +
          (st.event ? `<br><span style="color:#8fa2d8">${st.event}</span>` : '');
      }
    }
  } catch (e) {}
  try {
    const feed = await (await fetch('life/feed.json?t=' + Date.now())).json();
    const el2 = document.getElementById('life-feed');
    if (el2) {
      el2.innerHTML = (feed || []).slice(0, 3).map(x => {
        const d = new Date(x.ts * 1000);
        return `<div style="margin-bottom:6px"><span style="color:#6f7fae">${d.getMonth()+1}/${d.getDate()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}</span><br>${x.text}</div>`;
      }).join('') || '<span style="color:#6f7fae">还没发过说说</span>';
    }
  } catch (e) {}
}
refreshLife();
setInterval(refreshLife, 15000);
/* 实时时钟：与真实 24 小时对应 */
function tickLifeClock() {
  const el = document.getElementById('life-clock');
  if (!el) return;
  const d = new Date();
  const hh = String(d.getHours()).padStart(2, '0');
  const mm = String(d.getMinutes()).padStart(2, '0');
  const ss = String(d.getSeconds()).padStart(2, '0');
  el.textContent = `现在 ${hh}:${mm}:${ss}`;
}
tickLifeClock();
setInterval(tickLifeClock, 1000);
/* ---------- 24 小时时间轴（可调出） ---------- */
const TL_COLORS = {
  "睡觉": "#33405f", "赖床": "#4a5a86", "吃早饭": "#c8a14a", "做事/写东西": "#5a7fc0",
  "做午饭": "#c88a4a", "午休，躺着发呆": "#6b7fb0", "忙手上的事": "#5a7fc0",
  "做晚饭": "#c88a4a", "放松，看外面": "#7a6fc0", "躺着刷手机": "#9a6fc0",
  "准备睡觉": "#3d4a6b"
};
let tlInited = false, tlTimer = null;

async function buildTimeline() {
  const bar = document.getElementById('tl-bar');
  const ticks = document.getElementById('tl-ticks');
  const legend = document.getElementById('tl-legend');
  if (!bar) return;
  try {
    const d = await (await fetch('life/schedule.json?t=' + Date.now())).json();
    const sch = d.schedule || [];
    bar.innerHTML = '';
    legend.innerHTML = '';
    for (const s of sch) {
      const w = ((s.to - s.from) / 24) * 100;
      const col = s.dynamic ? '#b07cff' : (TL_COLORS[s.activity] || '#57678f');
      const seg = document.createElement('div');
      seg.style.cssText = `position:absolute;left:${(s.from/24)*100}%;width:${w}%;top:0;bottom:0;background:${col};opacity:.85`;
      seg.title = `${s.from}:00-${s.to}:00 ${s.location} · ${s.activity}` + (s.reason ? `（${s.reason}）` : '');
      bar.appendChild(seg);
      legend.innerHTML += `<div><span style="display:inline-block;width:9px;height:9px;border-radius:2px;background:${col};margin-right:6px"></span>${s.from}–${s.to} ${s.activity}` + (s.reason ? `<span style="color:#8f7ac0">（${s.reason}）</span>` : '') + `</div>`;
    }
    ticks.innerHTML = '';
    for (let h = 0; h <= 24; h += 3) {
      const t = document.createElement('span');
      t.style.cssText = `position:absolute;left:${(h/24)*100}%;transform:translateX(-50%)`;
      t.textContent = h === 24 ? '' : h + '点';
      ticks.appendChild(t);
    }
    tlInited = true;
    updateTimelineNow();
  } catch (e) {}
}

function updateTimelineNow() {
  const bar = document.getElementById('tl-bar');
  const nowEl = document.getElementById('tl-now');
  if (!bar || !nowEl) return;
  const d = new Date();
  const h = d.getHours() + d.getMinutes() / 60;
  let marker = document.getElementById('tl-marker');
  if (!marker) {
    marker = document.createElement('div');
    marker.id = 'tl-marker';
    marker.style.cssText = 'position:absolute;top:-3px;bottom:-3px;width:2px;background:#fff;box-shadow:0 0 8px #fff;z-index:3';
    bar.appendChild(marker);
  }
  marker.style.left = `${(h / 24) * 100}%`;
  nowEl.textContent = `现在 ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
}

document.getElementById('tlBtn')?.addEventListener('click', () => {
  const p = document.getElementById('tlPanel');
  if (!p) return;
  const show = p.style.display === 'none' || !p.style.display;
  p.style.display = show ? 'block' : 'none';
  if (show && !tlInited) buildTimeline();
  if (show) { if (!tlTimer) tlTimer = setInterval(updateTimelineNow, 1000); }
  else { clearInterval(tlTimer); tlTimer = null; }
});
document.getElementById('tl-close')?.addEventListener('click', () => {
  document.getElementById('tlPanel').style.display = 'none';
  clearInterval(tlTimer); tlTimer = null;
});
/* ---------- 新记忆自动刷新 ---------- */
setInterval(async () => {
  try {
    const list = await (await fetch('memory_stars.json?t=' + Date.now())).json();
    const cur = (typeof memPoints !== 'undefined' && memPoints)
      ? memPoints.geometry.getAttribute('position').count : 0;
    if (list.length !== cur) location.reload();
  } catch (e) { /* 忽略 */ }
}, 20000);
/* ---------- 连线 + 可拖动面板 ---------- */
let selectedMem = null;
const lineCv = document.createElement('canvas');
lineCv.style.cssText = 'position:fixed;left:0;top:0;width:100vw;height:100vh;pointer-events:none;z-index:19;';
document.body.appendChild(lineCv);
const lineCtx = lineCv.getContext('2d');
function resizeLineCv(){ lineCv.width = innerWidth; lineCv.height = innerHeight; }
resizeLineCv();
addEventListener('resize', resizeLineCv);

const _memV = new THREE.Vector3();
function drawMemLine() {
  lineCtx.clearRect(0, 0, lineCv.width, lineCv.height);
  if (selectedMem === null || !memPoints || memPanel.style.display !== 'block') return;
  if (selectedMem === -1) {
    _memV.set(0, 0, 0);
  } else {
    const pa = memPoints.geometry.getAttribute('position');
    _memV.set(pa.getX(selectedMem), pa.getY(selectedMem), pa.getZ(selectedMem));
    memPoints.localToWorld(_memV);
  }
  _memV.project(camera);
  if (_memV.z > 1) return;
  const sx = (_memV.x * 0.5 + 0.5) * innerWidth;
  const sy = (-_memV.y * 0.5 + 0.5) * innerHeight;
  const r = memPanel.getBoundingClientRect();
  const tx = Math.max(r.left, Math.min(sx, r.right));
  const ty = Math.max(r.top, Math.min(sy, r.bottom));
  lineCtx.strokeStyle = 'rgba(150,195,255,0.55)';
  lineCtx.lineWidth = 1.1;
  lineCtx.beginPath(); lineCtx.moveTo(sx, sy); lineCtx.lineTo(tx, ty); lineCtx.stroke();
  lineCtx.strokeStyle = 'rgba(200,225,255,0.95)';
  lineCtx.lineWidth = 1.4;
  lineCtx.beginPath(); lineCtx.arc(sx, sy, 4.5, 0, 7); lineCtx.stroke();
}

/* 面板可拖动 */
let memDrag = null;
memPanel.addEventListener('mousedown', e => {
  const r = memPanel.getBoundingClientRect();
  memPanel.style.left = r.left + 'px';
  memPanel.style.top = r.top + 'px';
  memPanel.style.right = 'auto';
  memPanel.style.bottom = 'auto';
  memDrag = { x: e.clientX - r.left, y: e.clientY - r.top };
  memPanel.style.cursor = 'grabbing';
  e.preventDefault();
});
addEventListener('mousemove', e => {
  if (!memDrag) return;
  memPanel.style.left = (e.clientX - memDrag.x) + 'px';
  memPanel.style.top = (e.clientY - memDrag.y) + 'px';
});
addEventListener('mouseup', () => { memDrag = null; memPanel.style.cursor = 'grab'; });
memPanel.style.cursor = 'grab';

/* ============================================================
   主循环
   ============================================================ */
const clock = new THREE.Clock();
let elapsed = 0, introT = 0, frames = 0, fpsT = 0;
const ease = t => 1 - Math.pow(1 - t, 3);

function tick() {
  requestAnimationFrame(tick);
  const dt = Math.min(clock.getDelta(), 0.05);
  elapsed += dt;

  if (spinOn) galaxy.rotation.y += dt * 0.012 * timeScale;
  bg.rotation.y += dt * 0.0012;

  starMat.uniforms.uTime.value = elapsed;
  brightMat.uniforms.uTime.value = elapsed;
  hazeMat.uniforms.uTime.value = elapsed;
  dustMat.uniforms.uTime.value = elapsed;
  if (bg.children[0]) bg.children[0].material.uniforms.uTime.value = elapsed;
  if (memMat) memMat.uniforms.uTime.value = elapsed;


  // 星云缓慢呼吸
  for (const sp of nebGroup.children) {
    sp.material.opacity = sp.userData.base * (0.8 + 0.2 * Math.sin(elapsed * 0.35 + sp.userData.phase));
  }

  // 太阳标记脉冲
  for (const sp of markerGroup.children) {
    if (sp.userData.isRing) {
      const t = (elapsed % 2.4) / 2.4;
      const s = 2 + t * 6;
      sp.scale.set(s, s, 1);
      sp.material.opacity = 0.85 * (1 - t) * (1 - t);
    }
  }

  // 开场镜头
  if (introT < 1) {
    introT = Math.min(1, introT + dt / 5.0);
    camera.position.lerpVectors(CAM_FROM, CAM_TO, ease(introT));
    camera.lookAt(0, 0, 0);
    if (introT >= 1) { controls.enabled = true; controls.update(); }
  } else {
    controls.update();
  }

  composer.render();
  // 中心主人公名字跟随银河中心
  {
    const cn = document.getElementById('centername');
    if (cn) {
      const v = new THREE.Vector3(0, 0, 0).project(camera);
      const sx = (v.x * 0.5 + 0.5) * innerWidth;
      const sy = (-v.y * 0.5 + 0.5) * innerHeight;
      cn.style.left = sx + 'px';
      cn.style.top = sy + 'px';
      const dist = camera.position.length();
      const op = Math.max(0.62, Math.min(1.0, 150 / Math.max(30, dist)));
      cn.style.opacity = op.toFixed(2);
    }
  }
  drawMemLine();
  updateLabels();

  frames++; fpsT += dt;
  if (fpsT >= 1) { $('fps').textContent = frames + ' FPS'; frames = 0; fpsT = 0; }
}

// 侧栏收起 / 展开
(function () {
  const life = document.getElementById('life');
  const lifeToggle = document.getElementById('lifeToggle');
  const panel = document.getElementById('panel');
  const panelToggle = document.getElementById('panelToggle');
  const lifeClose = document.getElementById('life-close');
  const panelClose = document.getElementById('panel-close');
  if (lifeClose && life && lifeToggle) {
    lifeClose.addEventListener('click', () => { life.style.display = 'none'; lifeToggle.style.display = 'block'; });
    lifeToggle.addEventListener('click', () => { life.style.display = 'block'; lifeToggle.style.display = 'none'; });
  }
  if (panelClose && panel && panelToggle) {
    panelClose.addEventListener('click', () => { panel.style.display = 'none'; panelToggle.style.display = 'block'; });
    panelToggle.addEventListener('click', () => { panel.style.display = ''; panelToggle.style.display = 'none'; });
  }
})();

// 记忆详情：× 关闭
(function () {
  const box = document.getElementById('memp');
  const close = document.getElementById('memp-close');
  if (box && close) {
    close.addEventListener('click', (ev) => {
      ev.stopPropagation();
      box.style.display = 'none';
      selectedMem = null;
    });
  }
})();

// 查找记忆：收起 / 展开
(function () {
  const box = document.getElementById('memSearch');
  const toggle = document.getElementById('memSearchToggle');
  const close = document.getElementById('memSearchClose');
  if (box && toggle && close) {
    close.addEventListener('click', () => { box.style.display = 'none'; toggle.style.display = 'block'; });
    toggle.addEventListener('click', () => { box.style.display = 'block'; toggle.style.display = 'none'; });
  }
})();

// 进入星图默认收起：查找记忆、控制台（只保留左侧她的此刻）
(function collapseByDefault() {
  const box = document.getElementById('memSearch');
  const toggle = document.getElementById('memSearchToggle');
  const panel = document.getElementById('panel');
  const panelToggle = document.getElementById('panelToggle');
  if (box && toggle) { box.style.display = 'none'; toggle.style.display = 'block'; }
  if (panel && panelToggle) { panel.style.display = 'none'; panelToggle.style.display = 'block'; }
})();

// 手机端：替换底部操作提示
if ('ontouchstart' in window) {
  const h = document.getElementById('hints');
  if (h) {
    h.innerHTML = '<span>单指 <em>旋转</em></span><span>双指 <em>缩放/平移</em></span>'
      + '<span class="sep"></span><span>点击星星 <em>查看记忆</em></span>';
  }
}

/* ---------- 星图外观调节 ---------- */
function applyStarBright(v) {
  try {
    starMat.uniforms.uOpacity.value = 0.86 * v;
    brightMat.uniforms.uOpacity.value = 0.74 * v;
    if (bgMat) bgMat.uniforms.uOpacity.value = 0.55 * v;
    if (memMat) memMat.uniforms.uOpacity.value = 0.86 * v;
  } catch (e) { }
}

function applyNebula(v) {
  try {
    for (const sp of nebGroup.children) {
      sp.material.opacity = sp.userData.base * v;
    }
    dustMat.uniforms.uOpacity.value = 0.12 * v;
    hazeMat.uniforms.uOpacity.value = 0.055 * v;
  } catch (e) { }
}

function applyStarSize(v) {
  try {
    const px = pxValue() * v;
    for (const m of [starMat, brightMat, hazeMat, dustMat]) m.uniforms.uPx.value = px;
    if (memMat) memMat.uniforms.uPx.value = px;
  } catch (e) { }
}

(function bindResetLook() {
  const btn = document.getElementById('resetLook');
  if (!btn) return;
  btn.onclick = () => {
    try {
      const b = $('rngBloom'); if (b) { b.value = 0.95; bloom.strength = 0.95; }
      const t = $('rngTime'); if (t) { t.value = 1; timeScale = 1; }
      const s = $('rngStar'); if (s) { s.value = 1; applyStarBright(1); }
      const n = $('rngNebula'); if (n) { n.value = 1; applyNebula(1); }
      const sz = $('rngSize'); if (sz) { sz.value = 1; applyStarSize(1); }
      const sp = $('rngSpin'); if (sp) { sp.value = 1; controls.autoRotateSpeed = 0.22; }
      $('chkSpin').checked = true; spinOn = true;
      $('chkCruise').checked = true; controls.autoRotate = true;
      // 恢复到开场结束后的舒适视角（不是开场前的远景）
      camera.position.set(38, 62, 158);
      controls.target.set(0, 0, 0);
      controls.update();
    } catch (e) { }
  };
})();

(function bindLookControls() {
  const star = $('rngStar'), neb = $('rngNebula'), size = $('rngSize'), spin = $('rngSpin');
  if (star) star.oninput = e => applyStarBright(parseFloat(e.target.value));
  if (neb) neb.oninput = e => applyNebula(parseFloat(e.target.value));
  if (size) size.oninput = e => applyStarSize(parseFloat(e.target.value));
  if (spin) spin.oninput = e => { controls.autoRotateSpeed = 0.22 * parseFloat(e.target.value); };
})();

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
  composer.setSize(innerWidth, innerHeight);
  const px = pxValue();
  for (const m of [starMat, brightMat, hazeMat, dustMat]) m.uniforms.uPx.value = px;
});

/* ---------- 启动 ---------- */
$('starCount').textContent = (TOTAL_STARS + N_BRIGHT).toLocaleString('en-US') + ' 恒星';
$('loading-count').textContent = '400';
tick();
requestAnimationFrame(() => {
  document.getElementById('loading').classList.add('hide');
  document.body.classList.add('ready');
});
