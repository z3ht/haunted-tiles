import { Types, AUTO, Scale } from 'phaser';

export type GameConfig = Types.Core.GameConfig;

export const defaultConfig: GameConfig = {
  type: AUTO,

  width: 1920,
  height: 1080,
  scale: {
    mode: Scale.WIDTH_CONTROLS_HEIGHT,
    autoCenter: Scale.CENTER_HORIZONTALLY,
  },

  // physics: {
  //   default: 'arcade',
  //   arcade: {
  //     gravity: { y: 100 }
  //   }
  // }

  banner: false,
  backgroundColor: '#ff00ff', //white for now

  seed: [Math.random().toString()],
}
