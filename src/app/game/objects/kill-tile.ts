import { Coord, ILocation, INeighbor, IVisitor, TileState, WorldPosition } from './interfaces';

export class KillTile implements ILocation {
  index: number = -1;
  state: TileState = TileState.Broken;

  constructor(public coord: Coord, public neighbor: INeighbor, private position: WorldPosition) {}

  acceptVisitor(visitor: IVisitor): boolean {
    visitor.die();
    return true;
  }
  exitVisitor(visitor: IVisitor) {
    // no one exits from the kill tile!
  }
  getPosition(): WorldPosition {
    return this.position;
  }

  setState(tile:TileState){
    return;
  }

}
