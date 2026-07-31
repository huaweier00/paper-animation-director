import { finite } from "../deterministic.js";


const LAYER_KINDS = new Set(["plane", "shape", "model"]);
const MOTION_KINDS = new Set(["static", "parallax", "bob", "sway"]);


function vector(value, size, fallback) {
  if (!Array.isArray(value) || value.length !== size) return [...fallback];
  return value.map((item, index) => finite(item, fallback[index]));
}


function normalizeMotion(value) {
  const input = value && typeof value === "object" ? value : {};
  const kind = MOTION_KINDS.has(input.kind) ? input.kind : "static";
  return {
    kind,
    axis: input.axis === "y" || input.axis === "z" ? input.axis : "x",
    amplitude: finite(input.amplitude, 0),
    frequency: finite(input.frequency, 1),
    phase: finite(input.phase, 0),
  };
}


function normalizeSceneManifest(manifest) {
  if (!manifest || typeof manifest !== "object" || manifest.schema_version !== 1) {
    throw new TypeError("Three declarative scene requires schema_version 1");
  }
  const cameraInput = manifest.camera || {};
  const camera = {
    kind: cameraInput.kind === "orthographic" ? "orthographic" : "perspective",
    fov: finite(cameraInput.fov_degrees, 34),
    near: finite(cameraInput.near, 0.1),
    far: finite(cameraInput.far, 100),
    position: vector(cameraInput.position, 3, [0, 0, 10]),
    lookAt: vector(cameraInput.look_at, 3, [0, 0, 0]),
  };
  const ids = new Set();
  const layers = (Array.isArray(manifest.layers) ? manifest.layers : []).map((entry, index) => {
    if (!entry || typeof entry !== "object") throw new TypeError(`layers[${index}] must be an object`);
    const id = String(entry.id || "").trim();
    if (!id || ids.has(id)) throw new Error(`layers[${index}] requires a unique id`);
    ids.add(id);
    const kind = String(entry.kind || "");
    if (!LAYER_KINDS.has(kind)) throw new Error(`layers[${index}] has unsupported kind ${kind}`);
    return {
      id,
      kind,
      depth: finite(entry.depth, 0),
      position: vector(entry.position, 2, [0, 0]),
      scale: vector(entry.scale, 3, [1, 1, 1]),
      size: vector(entry.size, 2, [1, 1]),
      points: Array.isArray(entry.points)
        ? entry.points.map((point) => vector(point, 2, [0, 0]))
        : [],
      source: typeof entry.source === "string" ? entry.source : null,
      required: entry.required !== false,
      material: {
        color: entry.material?.color || "#ffffff",
        roughness: finite(entry.material?.roughness, 0.93),
        opacity: finite(entry.material?.opacity, 1),
      },
      motion: normalizeMotion(entry.motion),
    };
  });
  if (layers.length === 0) throw new Error("Three declarative scene requires at least one layer");
  return {
    sceneId: String(manifest.scene_id || "declarative-paper-scene"),
    camera,
    lights: Array.isArray(manifest.lights) ? manifest.lights : [],
    layers,
  };
}


function materialFor(THREE, spec) {
  return new THREE.MeshStandardMaterial({
    color: new THREE.Color(spec.color),
    roughness: spec.roughness,
    metalness: 0,
    opacity: spec.opacity,
    transparent: spec.opacity < 1,
    side: THREE.DoubleSide,
  });
}


function shapeGeometry(THREE, points) {
  if (points.length < 3) throw new Error("shape layers require at least three points");
  const shape = new THREE.Shape();
  shape.moveTo(points[0][0], points[0][1]);
  for (const point of points.slice(1)) shape.lineTo(point[0], point[1]);
  shape.closePath();
  return new THREE.ShapeGeometry(shape);
}


function applyMotion(object, layer, time) {
  const { kind, axis, amplitude, frequency, phase } = layer.motion;
  const base = object.userData.paperBasePosition;
  object.position.set(base[0], base[1], base[2]);
  if (kind === "static") return;
  const wave = Math.sin(time * frequency + phase) * amplitude;
  if (kind === "sway") {
    object.rotation.z = wave;
  } else {
    object.position[axis] += kind === "bob" ? Math.abs(wave) : wave;
  }
}


async function createLayer({ THREE, layer, loaders }) {
  let object;
  if (layer.kind === "plane") {
    object = new THREE.Mesh(
      new THREE.PlaneGeometry(layer.size[0], layer.size[1]),
      materialFor(THREE, layer.material),
    );
  } else if (layer.kind === "shape") {
    object = new THREE.Mesh(
      shapeGeometry(THREE, layer.points),
      materialFor(THREE, layer.material),
    );
  } else {
    if (!layer.source || typeof loaders?.loadModel !== "function") {
      if (!layer.required) return null;
      throw new Error(`model layer ${layer.id} requires loaders.loadModel and a local source`);
    }
    object = await loaders.loadModel(layer.source);
  }
  object.name = layer.id;
  object.position.set(layer.position[0], layer.position[1], layer.depth);
  object.scale.set(...layer.scale);
  object.userData.paperBasePosition = [layer.position[0], layer.position[1], layer.depth];
  return object;
}


function addLights(THREE, scene, lights) {
  for (const item of lights) {
    if (!item || typeof item !== "object") continue;
    const color = new THREE.Color(item.color || "#ffffff");
    const intensity = finite(item.intensity, 1);
    let light;
    if (item.kind === "directional") light = new THREE.DirectionalLight(color, intensity);
    else if (item.kind === "point") light = new THREE.PointLight(color, intensity);
    else light = new THREE.AmbientLight(color, intensity);
    const position = vector(item.position, 3, [0, 0, 1]);
    light.position?.set?.(...position);
    light.name = String(item.id || item.kind || "light");
    scene.add(light);
  }
}


async function createDeclarativePaperScene({ THREE, width, height, manifest, loaders = {} }) {
  const spec = normalizeSceneManifest(manifest);
  const scene = new THREE.Scene();
  const camera = spec.camera.kind === "orthographic"
    ? new THREE.OrthographicCamera(-5, 5, 5 * height / width, -5 * height / width, spec.camera.near, spec.camera.far)
    : new THREE.PerspectiveCamera(spec.camera.fov, width / height, spec.camera.near, spec.camera.far);
  camera.position.set(...spec.camera.position);
  const target = new THREE.Vector3(...spec.camera.lookAt);
  camera.lookAt(target);
  addLights(THREE, scene, spec.lights);
  const layers = [];
  for (const layer of spec.layers) {
    const object = await createLayer({ THREE, layer, loaders });
    if (!object) continue;
    layers.push({ layer, object });
    scene.add(object);
  }
  function updateAt(localTime) {
    const time = Math.max(0, finite(localTime, 0));
    for (const entry of layers) applyMotion(entry.object, entry.layer, time);
    camera.lookAt(target);
  }
  return {
    scene,
    camera,
    updateAt,
    metadata: {
      sceneId: spec.sceneId,
      layerCount: layers.length,
    },
    dispose() {
      scene.traverse((object) => {
        object.geometry?.dispose?.();
        const materials = Array.isArray(object.material) ? object.material : [object.material];
        for (const material of materials) material?.dispose?.();
      });
    },
  };
}


export {
  LAYER_KINDS,
  MOTION_KINDS,
  createDeclarativePaperScene,
  normalizeMotion,
  normalizeSceneManifest,
};
