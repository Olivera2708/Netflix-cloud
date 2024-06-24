import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';
import { provideHttpClient } from "@angular/common/http";
import { MatMenuModule } from "@angular/material/menu";
import { MatButtonModule } from "@angular/material/button";
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { Interceptor } from './authentication/interceptor/interceptro';

@NgModule({
  declarations: [
  ],
  imports: [
    AppComponent,
    BrowserModule,
    MatMenuModule,
    MatButtonModule,
    CommonModule,
    FormsModule,
    HttpClientModule
  ],
  providers: [
    { provide: HTTP_INTERCEPTORS, useClass: Interceptor, multi: true },
    provideHttpClient()
  ],
  bootstrap: []
})
export class AppModule { }
