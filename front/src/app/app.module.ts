import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
// import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { AppComponent } from './app.component';
import { MatMenuModule } from "@angular/material/menu";
import { MatButtonModule } from "@angular/material/button";
// import { FormsModule } from '@angular/forms';
// import { CommonModule } from '@angular/common';
// import { RouterModule } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
// import { provideHttpClient, withInterceptorsFromDi, withInterceptors, HTTP_INTERCEPTORS } from '@angular/common/http';
// import { Test2Interceptor } from './authentication/interceptor/test2.interceptor';
// import { Interceptor } from './authentication/interceptor/interceptor';

@NgModule({
  declarations: [
  ],
  imports: [
    AppComponent,
    BrowserModule,
    MatMenuModule,
    MatButtonModule,
  ],
  providers: [
    provideHttpClient()
  ],
  bootstrap: []
})
export class AppModule { }
