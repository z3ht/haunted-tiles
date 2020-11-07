import { Animations, Scene, Types } from 'phaser';

export const BroomWestFacingOrigin = {
  x: 144,
  y: 10
};
export const BroomEastFacingOrigin = {
  x: 8,
  y: 10,
}

export const SweepEastFacingHandPositions = [
  {
    x: 35,
    y: -60,
  },
  {
    x: 55,
    y: -52,
  },
  {
    x: 72,
    y: -47,
  },
];

export const IdleEastFacingHandPositions = [
  {
    x: 43,
    y: -55,
  },
  {
    x: 42,
    y: -54,
  },
  {
    x: 40,
    y: -52,
  },
];

export const RestWestFacingHandPositions = [
  {
    x: -43,
    y: -56,
  },
  {
    x: -43,
    y: -56,
  },
  {
    x: -43,
    y: -55,
  },
];

export const BroomAtlas = 'broom';
const assetPath = 'assets/sprites';

export function loadBroomAssets(scene: Scene) {
  scene.load.multiatlas(BroomAtlas, `${assetPath}/broom.json`, assetPath);
}

export function createBroomAnimFrames(anims: Animations.AnimationManager) {
  const start = 0;
  const zeroPad = 1;
  const suffix = '.png';
  const animFrameMap: Record<string, Types.Animations.AnimationFrame[]> = {
    ['broom-sweep']: anims.generateFrameNames(BroomAtlas, { prefix: `broom-`, end: 4, start, zeroPad, suffix}),
  };

  anims.create({ key: `broom_sweep`, frames: animFrameMap['broom-sweep'], frameRate:4, yoyo: true});
}

