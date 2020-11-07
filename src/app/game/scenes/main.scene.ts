import { Scene } from 'phaser';
import { squareGrid } from '../objects/grid';

import { loadMonsterAssets, createAllMonsterAnimFrames } from '../objects/monster'
import { MatchEventArgs, MatchEvent } from '../objects/interfaces';

import { GameManager } from '../objects/game-manager';
import { loadBackgroundAssets, Background } from '../objects/background';
import { loadTileAssets } from '../objects/tile';
import { createAllGameEndAnimFrames, GameEnd, loadGameEndAssets } from '../objects/game-end';

export const MainKey = 'main';

export class MainScene extends Scene {
  match: GameManager;
  background: Background;
  gameEnd: GameEnd;

  constructor() {
    super({ key: MainKey });
    this.match = new GameManager();
  }

  create() {
    // initialize all the animations
    createAllMonsterAnimFrames(this.anims);
    createAllGameEndAnimFrames(this.anims);
    this.background = new Background(this);
    this.gameEnd = new GameEnd();
    const grid = squareGrid(this, this.scale, 7);
    this.match.initGrid(grid);
  }

  preload() {
    loadBackgroundAssets(this);
    loadMonsterAssets(this);
    loadTileAssets(this);
    loadGameEndAssets(this);
  }

  update(time: number, dt: number) {
    this.background.update(dt); 
    this.gameEnd.update(dt);
  }
}
