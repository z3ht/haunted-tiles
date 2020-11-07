import { Game, Core, Scenes } from 'phaser';
import { GameConfig, defaultConfig } from './config';
import { MainScene, MainKey } from './scenes/main.scene';

export { Game } from 'phaser';
export { GameConfig } from './config';
export { Side } from './objects/interfaces';
export { TeamInfo } from './objects/game-manager';
export { MainKey } from './scenes/main.scene';

export const GameEvent = Core.Events;
export const SceneEvent = Scenes.Events;

export function createGame(config: GameConfig): Promise<Game> {
  return new Promise(resolve => {
    const game = new Game({ ...defaultConfig, scene: [MainScene], ...config });
    game.events.on(Core.Events.READY, () => {
      game.scene.pause(MainKey); // immediately pause the game
      resolve(game);
    })
  });
}
