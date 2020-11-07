import { Injectable } from '@angular/core';

@Injectable({
    providedIn: 'root'
})

export class RoundManagerService {
    public numRounds: number = 3;
    public completedRounds: number = 0;

    public homeRoundWins: number = 0;
    public awayRoundWins: number = 0;
    public roundDraws: number = 0;

    reset() {
        this.completedRounds = 0;
        this.homeRoundWins = 0;
        this.awayRoundWins = 0;
        this.roundDraws = 0;
    }

}
