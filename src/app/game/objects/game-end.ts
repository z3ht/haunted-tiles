import { GameObjects, Scene, Math as PMath, Animations, Types, Textures } from 'phaser';
import { BroomAtlas, BroomEastFacingOrigin, BroomWestFacingOrigin, createBroomAnimFrames, IdleEastFacingHandPositions, loadBroomAssets, RestWestFacingHandPositions, SweepEastFacingHandPositions } from './broom';
import { GameWinningSide, MonsterType, Side } from './interfaces';
import { MonstersAtlas, MonsterColor } from './monster';

export const HomeAtlas = 'home';
export const AwayAtlas = 'away';
export const WinsAtlas = 'wins';
export const DrawAtlas = 'draw';
const assetsPath = 'assets/sprites';

export function loadGameEndAssets(scene: Scene) {
  scene.load.multiatlas(HomeAtlas, `${assetsPath}/home.json`, assetsPath);
  scene.load.multiatlas(AwayAtlas, `${assetsPath}/away.json`, assetsPath);
  scene.load.multiatlas(WinsAtlas, `${assetsPath}/wins.json`, assetsPath);
  scene.load.multiatlas(DrawAtlas, `${assetsPath}/draw.json`, assetsPath);
  loadBroomAssets(scene);
}

enum VictoryAnim {
  BroomSweepMove = 'broom_sweep_move',
  BroomSweepIdle = 'broom_sweep_idle',
}

export function createVictoryAnimFrames(
  anims: Animations.AnimationManager, 
  monster: MonsterType
) {
  const start = 0;
  const zeroPad = 3;
  const suffix = '.png';
  const animFrameMap: Record<string, Types.Animations.AnimationFrame[]> = {
    [VictoryAnim.BroomSweepIdle]: anims.generateFrameNames(
      MonstersAtlas,
      { 
        prefix: `${monster}/idle/Idle_`,
        end: 11,
        start,
        zeroPad,
        suffix
      }
    ),
    [VictoryAnim.BroomSweepMove]: anims.generateFrameNames(
      MonstersAtlas,
      { 
        prefix: `${monster}/broom-sweep-move/BroomSweepMove_`,
        end: 6,
        start,
        zeroPad,
        suffix
      }
    ),
  };

  anims.create({
    key: `${monster}_${VictoryAnim.BroomSweepIdle}`,
    frames: animFrameMap[VictoryAnim.BroomSweepIdle],
    frameRate: 15,
    repeat: -1
  });
  anims.create({
    key: `${monster}_${VictoryAnim.BroomSweepMove}`,
    frames: animFrameMap[VictoryAnim.BroomSweepMove],
    frameRate: 12,
    repeat: -1,
    yoyo: true
  });
}

export function createAllGameEndAnimFrames(anims: Animations.AnimationManager) {
  Object.values(MonsterType).forEach(monster => {
    createVictoryAnimFrames(anims, monster);
  });
  createBroomAnimFrames(anims);
}

export class GameEnd {
  victoryMonster: GameObjects.Sprite;
  defeatMonster: GameObjects.Sprite;
  broom: GameObjects.Sprite;
  homeText: GameObjects.Sprite;
  awayText: GameObjects.Sprite;
  winsText: GameObjects.Sprite;
  drawText: GameObjects.Sprite;
  isGameOver = false;  
  isDraw = false;
  private victoryType: MonsterType;
  private gameEndTime = 0;
  private gameEndLoop = 1500;  
  private floorAxisY = 1000;

  init(scene: Scene, winningSide: GameWinningSide, victoryMonsterType: MonsterType, defeatMonsterType: MonsterType) {
    this.isGameOver = true;
    if (winningSide === GameWinningSide.Draw) {
      this.isDraw = true;
      this.drawText = new GameObjects.Sprite(
        scene,
        650,
        200,
        'draw',
        '1.png'
      );
      this.drawText.scaleX = 2;
      this.drawText.scaleY = 2;
      scene.add.existing(this.drawText);
      this.victoryMonster = new GameObjects.Sprite(
        scene, 
        800, 
        this.floorAxisY - 130, 
        MonstersAtlas, 
        `${victoryMonsterType}/die/Die_008.png`
      );  
      this.victoryMonster.flipX = true;
      this.victoryMonster.setRotation(-2.6);
  
      this.defeatMonster = new GameObjects.Sprite(
        scene,
        1200,
        this.floorAxisY + 20,
        MonstersAtlas,
        `${defeatMonsterType}/die/Die_008.png`
      );
      this.defeatMonster.flipX = true;
      scene.add.existing(this.victoryMonster);
      scene.add.existing(this.defeatMonster);
    } else {
      this.winsText = new GameObjects.Sprite(
        scene,
        1000,
        200,
        'wins',
        '1.png'
      );
      this.setColor(this.winsText, victoryMonsterType);
      this.winsText.scaleX = 2;
      this.winsText.scaleY = 2;
      scene.add.existing(this.winsText);
  
      if (winningSide === GameWinningSide.Home) {
        this.homeText = new GameObjects.Sprite(
          scene,
          300,
          200,
          'home',
          '1.png'
        );    
        this.setColor(this.homeText, victoryMonsterType);
        this.homeText.scaleX = 2;
        this.homeText.scaleY = 2;
        scene.add.existing(this.homeText);
      } else if (winningSide === GameWinningSide.Away) {
        this.awayText = new GameObjects.Sprite(
          scene,
          300,
          200,
          'away',
          '1.png'
        );
        this.setColor(this.awayText, victoryMonsterType);
        this.awayText.scaleX = 2;
        this.awayText.scaleY = 2;
        scene.add.existing(this.awayText);
      }
  
      this.victoryMonster = new GameObjects.Sprite(
        scene, 
        300, 
        this.floorAxisY, 
        MonstersAtlas, 
        `${victoryMonsterType}/attack/Attack_000.png`
      );  
      this.victoryMonster.flipX = true;
  
      this.defeatMonster = new GameObjects.Sprite(
        scene,
        600,
        this.floorAxisY,
        MonstersAtlas,
        `${defeatMonsterType}/die/Die_008.png`
      );
  
      this.broom = new GameObjects.Sprite(
        scene,
        200 + SweepEastFacingHandPositions[0].x,
        this.floorAxisY + SweepEastFacingHandPositions[0].y,
        BroomAtlas,
      );
      this.broom.setDisplayOrigin(BroomEastFacingOrigin.x, BroomEastFacingOrigin.y);
  
      // this.broom.setRotation((this.testTime/1000) % (Math.PI * 2));
      this.broom.flipX = true;
  
      scene.add.existing(this.victoryMonster);
      scene.add.existing(this.defeatMonster);
      scene.add.existing(this.broom);
      this.victoryType = victoryMonsterType;
    } 

  }

  reset() {
    this.isGameOver = false;
    this.isDraw = false;
    this.victoryMonster?.destroy();
    this.defeatMonster?.destroy();
    this.broom?.destroy();
    this.winsText?.destroy();
    this.homeText?.destroy();
    this.awayText?.destroy();
    this.drawText?.destroy();
    this.gameEndTime = 0;
  }

  update(dt) {
    if (this.isGameOver) {
      if (!this.isDraw) {
        this.victoryUpdate(dt);
      }
    }
  }

  victoryUpdate(dt) {
    this.gameEndTime += dt;

    const i = this.gameEndTime > 0 ? Math.floor(this.gameEndTime / this.gameEndLoop) : 0;
    
    if ((i % 2) < 1 && i < 5) {
      const x = i / 2 * 300;
      this.moveVictoryMonster(300 + x, 600 + x);
      this.victoryMonster.play(`${this.victoryType}_broom_sweep_move`, true);
      this.broom.play('broom_sweep', true);
    } else if ((i % 2) > 0 && i < 5) {
      this.victoryMonster.play(`${this.victoryType}_idle`, true);
      this.broom.setFrame('broom-1.png');
      const t = Math.floor((this.gameEndTime % 1000) / 83.33333333333);
      let x = 0;
      if (i < 2) {
        x = 300;
      } else if (i < 4) {
        x = 600;
      }

      if (t === 0 || t === 11) {
        this.broom.setPosition(300 + x + IdleEastFacingHandPositions[0].x,  this.floorAxisY + IdleEastFacingHandPositions[0].y);
      } else if (t === 1 || t === 10) {
        this.broom.setPosition(300 + x + IdleEastFacingHandPositions[0].x,  this.floorAxisY + IdleEastFacingHandPositions[0].y);
      } else if (t === 2 || t === 9) {
        this.broom.setPosition(300 + x + IdleEastFacingHandPositions[1].x,  this.floorAxisY + IdleEastFacingHandPositions[1].y);
      } else if (t === 3 || t === 8) {
        this.broom.setPosition(300 + x + IdleEastFacingHandPositions[1].x,  this.floorAxisY + IdleEastFacingHandPositions[1].y);
      } else if (t === 4 || t === 7) {
        this.broom.setPosition(300 + x + IdleEastFacingHandPositions[2].x,  this.floorAxisY + IdleEastFacingHandPositions[2].y);
      } else if (t === 5 || t === 6) {
        this.broom.setPosition(300 + x + IdleEastFacingHandPositions[2].x,  this.floorAxisY + IdleEastFacingHandPositions[2].y);
      }
    } else if (i === 5) {
      this.victoryMonster.flipX = false;
      this.victoryMonster.play(`${this.victoryType}_idle`, true);
      this.broom.flipX = false;   
      this.broom.setDisplayOrigin(BroomWestFacingOrigin.x, BroomWestFacingOrigin.y);
      this.broom.setFrame('broom-3.png');
    } 

    if(i >= 5 && i < 6 ) {
      const t = Math.floor((this.gameEndTime % 1000) / 83.33333333333);

      if (t === 0 || t === 11) {
        this.broom.setPosition(1200 + RestWestFacingHandPositions[0].x,  this.floorAxisY + RestWestFacingHandPositions[0].y);
        this.broom.setRotation(0.8);
        this.broom.setFrame('broom-3.png');
      } else if (t === 1 || t === 10) {
        this.broom.setPosition(1200 + RestWestFacingHandPositions[0].x,  this.floorAxisY + RestWestFacingHandPositions[0].y);
        this.broom.setRotation(0.78);
        this.broom.setFrame('broom-3.png');
      } else if (t === 2 || t === 9) {
        this.broom.setPosition(1200 + RestWestFacingHandPositions[1].x,  this.floorAxisY + RestWestFacingHandPositions[1].y);
        this.broom.setRotation(0.76);
        this.broom.setFrame('broom-2.png');
      } else if (t === 3 || t === 8) {
        this.broom.setPosition(1200 + RestWestFacingHandPositions[1].x,  this.floorAxisY + RestWestFacingHandPositions[1].y);
        this.broom.setRotation(0.74);
        this.broom.setFrame('broom-2.png');
      } else if (t === 4 || t === 7) {
        this.broom.setPosition(1200 + RestWestFacingHandPositions[2].x,  this.floorAxisY + RestWestFacingHandPositions[2].y);
        this.broom.setRotation(0.72);
        this.broom.setFrame('broom-1.png');
      } else if (t === 5 || t === 6) {
        this.broom.setPosition(1200 + RestWestFacingHandPositions[2].x,  this.floorAxisY + RestWestFacingHandPositions[2].y);
        this.broom.setRotation(0.70);
        this.broom.setFrame('broom-1.png');
      }
    }

    if (i === 6) {
      this.broom.setFrame('broom-3.png');
      this.broom.setOrigin(0.5, 0.5);
    }

    if (i === 6) {
      this.broom.setRotation((this.gameEndTime/100) % (Math.PI * 2));
      const x = 1350 + 100 * Math.cos(-Math.PI + Math.PI * (this.gameEndTime % this.gameEndLoop) / (this.gameEndLoop + 200));
      const y = this.floorAxisY + 600 * Math.sin(0 - Math.PI * (this.gameEndTime % this.gameEndLoop) / (this.gameEndLoop + 200));
      this.broom.setPosition(x, y);
    }

    if (i === 7) {
      this.broom.setDisplayOrigin(BroomEastFacingOrigin.x, BroomEastFacingOrigin.y);
      this.broom.setPosition(1433, 840);
      let t = (this.gameEndTime % 1500) / 1250;
      t *= t;
      this.broom.setRotation(-1.9 - t);
    }
  }

  private moveVictoryMonster(x1: number, x2: number) {
    const normalizedTime = PMath.Clamp((this.gameEndTime % this.gameEndLoop) / this.gameEndLoop, 0, 1);
    const x = PMath.Interpolation.Linear([x1, x2], normalizedTime);
    this.victoryMonster.setPosition(x,  this.floorAxisY);
    this.defeatMonster.setPosition(x + 300,  this.floorAxisY);

    const t = Math.ceil((this.gameEndTime % 1000) / 142.857142857);

    if (t < 2) {
      this.broom.setPosition(x + SweepEastFacingHandPositions[0].x,  this.floorAxisY + SweepEastFacingHandPositions[0].y);        
    } else if (t < 4) {
      this.broom.setPosition(x + SweepEastFacingHandPositions[1].x,  this.floorAxisY + SweepEastFacingHandPositions[1].y);   
    } else {
      this.broom.setPosition(x + SweepEastFacingHandPositions[2].x,  this.floorAxisY + SweepEastFacingHandPositions[2].y);
    }
  }

  private setColor(sprite: GameObjects.Sprite, type: MonsterType) {
    switch(type) {
      case MonsterType.Bobo: {
        sprite.setTint(MonsterColor.Bobo);
        return;
      }
      case MonsterType.Triclops: {
        sprite.setTint(MonsterColor.Triclops);
        return;
      }
      case MonsterType.Spike: {
        sprite.setTint(MonsterColor.Spike);
        return;
      }
      case MonsterType.Goldy: {
        sprite.setTint(MonsterColor.Goldy);
        return;
      }
      case MonsterType.Grouchy: {
        sprite.setTint(MonsterColor.Grouchy);
        return;
      }
      case MonsterType.Pinky: {
        sprite.setTint(MonsterColor.Pinky);
        return;
      }
    }
  }
}
