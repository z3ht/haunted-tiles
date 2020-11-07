import { Component, OnInit, Input } from '@angular/core';
import { DomSanitizer, SafeResourceUrl} from '@angular/platform-browser';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'tyl-bracket',
  templateUrl: './bracket.component.html',
  styleUrls: ['./bracket.component.scss']
})
export class BracketComponent implements OnInit {

  constructor(private sanitizer: DomSanitizer, private activatedRoute: ActivatedRoute) { }

  @Input() key: string;
  url: SafeResourceUrl;

  ngOnInit(): void {
    this.activatedRoute.data.subscribe(data => {
      this.key = data.key;
    });
    this.url = this.sanitizer.bypassSecurityTrustResourceUrl(`https://challonge.com/${this.key}/module?show_tournament_name=1`);
  }

  

}
