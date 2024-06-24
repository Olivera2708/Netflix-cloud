import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';
import { provideHttpClient } from "@angular/common/http";
import { MatMenuModule } from "@angular/material/menu";
import { MatButtonModule } from "@angular/material/button";
import { NgModel } from '@angular/forms';
import { CommonModule } from '@angular/common';

@NgModule({
  declarations: [
  ],
  imports: [
    BrowserModule,
    AppComponent,
    MatMenuModule,
    MatButtonModule,
    NgModule,
    NgModel,
    CommonModule
  ],
  providers: [provideHttpClient()],
  bootstrap: []
})
export class AppModule { }
