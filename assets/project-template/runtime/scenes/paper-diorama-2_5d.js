import {
  seededRange,
  seededUnit,
} from "../deterministic.js";


function paperTexture(THREE, {
  id,
  base = "#d8b77b",
  fiber = "rgba(77, 45, 24, .16)",
  size = 256,
}) {
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const context = canvas.getContext("2d", { alpha: false });
  context.fillStyle = base;
  context.fillRect(0, 0, size, size);
  context.lineWidth = 0.7;
  for (let index = 0; index < 210; index += 1) {
    const x = seededRange(id, index * 4, 0, size);
    const y = seededRange(id, index * 4 + 1, 0, size);
    const length = seededRange(id, index * 4 + 2, 6, 34);
    const tilt = seededRange(id, index * 4 + 3, -0.25, 0.25);
    context.strokeStyle = fiber;
    context.globalAlpha = seededRange(id, index + 900, 0.16, 0.5);
    context.beginPath();
    context.moveTo(x, y);
    context.lineTo(x + length, y + length * tilt);
    context.stroke();
  }
  context.globalAlpha = 1;
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(1.6, 1.2);
  texture.needsUpdate = true;
  return texture;
}


function material(THREE, texture, {
  color = 0xffffff,
  roughness = 0.93,
  transparent = false,
  opacity = 1,
} = {}) {
  return new THREE.MeshStandardMaterial({
    map: texture,
    color,
    roughness,
    metalness: 0,
    transparent,
    opacity,
    side: THREE.DoubleSide,
  });
}


function cutout(THREE, points, depth, mat) {
  const shape = new THREE.Shape();
  shape.moveTo(points[0][0], points[0][1]);
  for (let index = 1; index < points.length; index += 1) {
    shape.lineTo(points[index][0], points[index][1]);
  }
  shape.closePath();
  const geometry = new THREE.ShapeGeometry(shape);
  const mesh = new THREE.Mesh(geometry, mat);
  mesh.position.z = depth;
  return mesh;
}


function disposeTree(root) {
  root.traverse((object) => {
    object.geometry?.dispose?.();
    const materials = Array.isArray(object.material) ? object.material : [object.material];
    for (const entry of materials) {
      entry?.map?.dispose?.();
      entry?.dispose?.();
    }
  });
}


export function createPaperDioramaScene({ THREE, width, height }) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(34, width / height, 0.1, 100);
  camera.position.set(0, 0.25, 10.2);

  const warmPaper = paperTexture(THREE, { id: "three-paper-warm", base: "#b9894f" });
  const palePaper = paperTexture(THREE, { id: "three-paper-pale", base: "#dfc99d" });
  const darkPaper = paperTexture(THREE, { id: "three-paper-dark", base: "#4e2d25" });
  const redPaper = paperTexture(THREE, { id: "three-paper-red", base: "#86372c" });

  const backdropMaterial = material(THREE, warmPaper, { color: 0x725039 });
  const backdrop = new THREE.Mesh(new THREE.PlaneGeometry(14.8, 8.4), backdropMaterial);
  backdrop.position.set(0, 0, -3.2);
  scene.add(backdrop);

  const farMountains = new THREE.Group();
  farMountains.position.z = -2.25;
  for (let index = 0; index < 5; index += 1) {
    const x = -6.6 + index * 3.1;
    const peak = 1.1 + seededUnit("far-mountain", index) * 1.25;
    farMountains.add(
      cutout(
        THREE,
        [[x - 2.0, -2.65], [x, peak], [x + 2.3, -2.65]],
        index * 0.008,
        material(THREE, palePaper, { color: 0x9c7958 }),
      ),
    );
  }
  scene.add(farMountains);

  const nearMountains = new THREE.Group();
  nearMountains.position.z = -1.25;
  for (let index = 0; index < 4; index += 1) {
    const x = -5.5 + index * 3.7;
    const peak = 0.7 + seededUnit("near-mountain", index) * 1.1;
    nearMountains.add(
      cutout(
        THREE,
        [[x - 2.6, -2.72], [x - 0.4, peak], [x + 2.4, -2.72]],
        index * 0.012,
        material(THREE, darkPaper, { color: 0x57352d }),
      ),
    );
  }
  scene.add(nearMountains);

  const moonMaterial = material(THREE, palePaper, {
    color: 0xffd799,
    transparent: true,
    opacity: 0.94,
  });
  const moon = new THREE.Mesh(new THREE.CircleGeometry(0.72, 48), moonMaterial);
  moon.position.set(3.55, 1.92, -0.7);
  scene.add(moon);

  const horse = new THREE.Group();
  horse.position.set(-1.65, -1.05, 0.08);
  const horseMaterial = material(THREE, redPaper, { color: 0x7e332a });
  const trimMaterial = material(THREE, palePaper, { color: 0xd6a86b });
  const body = new THREE.Mesh(new THREE.CircleGeometry(0.9, 48), horseMaterial);
  body.scale.set(1.6, 0.72, 1);
  horse.add(body);
  const neck = new THREE.Mesh(new THREE.PlaneGeometry(0.38, 1.28), horseMaterial);
  neck.position.set(1.05, 0.55, 0.015);
  neck.rotation.z = -0.34;
  horse.add(neck);
  const head = new THREE.Mesh(new THREE.CircleGeometry(0.38, 36), horseMaterial);
  head.scale.set(1.15, 0.72, 1);
  head.position.set(1.34, 1.02, 0.025);
  horse.add(head);
  const riderBody = new THREE.Mesh(new THREE.PlaneGeometry(0.52, 0.85), trimMaterial);
  riderBody.position.set(-0.1, 0.8, 0.04);
  horse.add(riderBody);
  const riderHead = new THREE.Mesh(new THREE.CircleGeometry(0.25, 32), trimMaterial);
  riderHead.position.set(-0.12, 1.36, 0.05);
  horse.add(riderHead);
  const legs = [];
  for (let index = 0; index < 4; index += 1) {
    const leg = new THREE.Mesh(new THREE.PlaneGeometry(0.18, 0.9), horseMaterial);
    leg.position.set(-0.92 + index * 0.62, -0.63, 0.02);
    leg.geometry.translate(0, -0.43, 0);
    legs.push(leg);
    horse.add(leg);
  }
  scene.add(horse);

  const foreground = new THREE.Group();
  foreground.position.z = 1.28;
  for (let index = 0; index < 13; index += 1) {
    const blade = cutout(
      THREE,
      [[-0.12, 0], [0, seededRange("grass", index, 0.55, 1.5)], [0.14, 0]],
      index * 0.004,
      material(THREE, darkPaper, { color: 0x2e211b }),
    );
    blade.position.set(-6.2 + index * 1.05, -3.15, index * 0.002);
    foreground.add(blade);
  }
  scene.add(foreground);

  const particleCount = 58;
  const positions = new Float32Array(particleCount * 3);
  const baseParticles = [];
  for (let index = 0; index < particleCount; index += 1) {
    baseParticles.push({
      x: seededRange("three-dust", index * 5, -5.5, 5.5),
      y: seededRange("three-dust", index * 5 + 1, -2.4, 2.7),
      z: seededRange("three-dust", index * 5 + 2, -0.8, 1.05),
      speed: seededRange("three-dust", index * 5 + 3, 0.06, 0.22),
      phase: seededRange("three-dust", index * 5 + 4, 0, Math.PI * 2),
    });
  }
  const particleGeometry = new THREE.BufferGeometry();
  particleGeometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  const particles = new THREE.Points(
    particleGeometry,
    new THREE.PointsMaterial({
      color: 0xe1ba78,
      size: 0.045,
      transparent: true,
      opacity: 0.5,
      depthWrite: false,
    }),
  );
  scene.add(particles);

  const ambient = new THREE.AmbientLight(0xffd8a8, 1.35);
  scene.add(ambient);
  const key = new THREE.DirectionalLight(0xffb36f, 3.3);
  key.position.set(-3.5, 5.5, 7);
  scene.add(key);
  const moonLight = new THREE.PointLight(0xff8d5a, 10, 12, 1.7);
  moonLight.position.copy(moon.position);
  moonLight.position.z = 2.2;
  scene.add(moonLight);

  const target = new THREE.Vector3(0, -0.15, -0.4);

  function updateAt(localTime) {
    const time = Math.max(0, localTime);
    camera.position.x = Math.sin(time * 0.52) * 0.34;
    camera.position.y = 0.25 + Math.cos(time * 0.41) * 0.12;
    camera.lookAt(target);
    farMountains.position.x = -camera.position.x * 0.16;
    nearMountains.position.x = -camera.position.x * 0.34;
    foreground.position.x = -camera.position.x * 0.72;
    moon.position.y = 1.92 + Math.sin(time * 0.62) * 0.08;
    moonLight.position.y = moon.position.y;
    horse.position.x = -1.65 + Math.sin(time * 0.74) * 1.22;
    horse.position.y = -1.05 + Math.abs(Math.sin(time * 2.25)) * 0.1;
    horse.rotation.z = Math.sin(time * 1.5) * 0.035;
    legs.forEach((leg, index) => {
      leg.rotation.z = Math.sin(time * 4.5 + index * Math.PI * 0.65) * 0.24;
    });
    for (let index = 0; index < particleCount; index += 1) {
      const particle = baseParticles[index];
      positions[index * 3] = particle.x + Math.sin(time * 0.36 + particle.phase) * 0.16;
      positions[index * 3 + 1] = -2.65
        + ((particle.y + 2.65 + time * particle.speed) % 5.6);
      positions[index * 3 + 2] = particle.z;
    }
    particleGeometry.attributes.position.needsUpdate = true;
    particles.material.opacity = 0.42 + Math.sin(time * 0.7) * 0.08;
    moonMaterial.opacity = 0.87 + Math.sin(time * 0.8) * 0.07;
  }

  return {
    scene,
    camera,
    updateAt,
    dispose() {
      disposeTree(scene);
      particleGeometry.dispose();
      particles.material.dispose();
    },
  };
}
