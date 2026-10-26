<?php

use Illuminate\Support\Facades\Route;
use Inertia\Inertia;

Route::get('/', fn () => Inertia::render('welcome', [
    'adminUrl' => route('filament.admin.pages.dashboard'),
]))->name('home');
