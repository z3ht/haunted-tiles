import { GameObjects, Scene } from 'phaser';

export const BackgroundAtlas = 'background';
const assetsPath = 'assets/sprites';

export function loadBackgroundAssets(scene: Scene) {
  scene.load.multiatlas(BackgroundAtlas, `${assetsPath}/background.json`, assetsPath);
}

export class Background extends GameObjects.Container {
  private tileSprites: GameObjects.TileSprite[] = [];

  constructor(scene: Scene) {
    super(scene);

    scene.add.existing(this);
    this.scale = 2;

    const backgroundImage = scene.add.sprite(0, 0, BackgroundAtlas, `1.png`);
    const cloudsAndBats = scene.add.tileSprite(0, 0, this.scene.scale.width, this.scene.scale.height, BackgroundAtlas, `2.png`);
    const moon = scene.add.sprite(0, 0, BackgroundAtlas, `3.png`);
    const backgroundGravesAndTrees = scene.add.sprite(0, 0, BackgroundAtlas, `4.png`);
    const fence = scene.add.sprite(0, 0, BackgroundAtlas, `5.png`);
    const foregroundGraves = scene.add.sprite(0, 0, BackgroundAtlas, `6.png`);
    const mausoleum = scene.add.sprite(0, 0, BackgroundAtlas, `7.png`);
    const hands = scene.add.sprite(0, 0, BackgroundAtlas, `8.png`);
    const foregroundDirt = scene.add.sprite(0, 0, BackgroundAtlas, `9.png`);

    this.add([
      backgroundImage,
      cloudsAndBats,
      moon,
      backgroundGravesAndTrees,
      fence,
      foregroundGraves,
      mausoleum,
      hands,
      foregroundDirt,
    ]);

    this.tileSprites.push(cloudsAndBats);
  }

  update(dt: number): void {
    this.tileSprites.forEach(sprite => sprite.tilePositionX -= 0.01 * dt);
  }
}
