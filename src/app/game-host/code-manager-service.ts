import { Injectable } from '@angular/core';

@Injectable({
    providedIn: 'root'
})

export class CodeManagerService {
    script = "//NOTE: This is for development purposes only, final submission should be done through the submission tab Fill in the contents of main with your strategy The contents of gameState and side can be found by viewing interfaces.ts IGameState and Side interfaces gameState represents the current state of the game (all tiles, all teams) side will tell you which team is yours main should return an array of MoveDirection's (also found in interfaces.ts) with size = # of monsters on one team to start/*\r\rfunction main(gameState, side){\r\tconst myTeam = gameState.teamStates[side];\r\treturn ['none', 'none', 'none'];\r}";
}
