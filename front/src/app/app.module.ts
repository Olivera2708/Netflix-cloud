import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';
import {provideHttpClient} from "@angular/common/http";

@NgModule({
  declarations: [

  ],
  imports: [
    BrowserModule,
    AppComponent
  ],
  providers: [provideHttpClient()],
  bootstrap: []
})
export class AppModule { }
