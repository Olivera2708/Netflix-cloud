import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';
import {provideHttpClient} from "@angular/common/http";
import {MatMenuModule} from "@angular/material/menu";
import {MatButtonModule} from "@angular/material/button";

@NgModule({
  declarations: [
  ],
  imports: [
    BrowserModule,
    AppComponent,
    MatMenuModule,
    MatButtonModule
  ],
  providers: [provideHttpClient()],
  bootstrap: []
})
export class AppModule { }
