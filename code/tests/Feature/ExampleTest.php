<?php

namespace Tests\Feature;

use Inertia\Testing\AssertableInertia as Assert;
use Tests\TestCase;

class ExampleTest extends TestCase
{
    /**
     * A basic test example.
     */
    public function test_the_application_returns_a_successful_response(): void
    {
        $response = $this->get('/');

        $response->assertOk()
            ->assertInertia(fn (Assert $page) => $page
                ->component('welcome')
                ->where('adminUrl', route('filament.admin.pages.dashboard'))
            );
    }

    public function test_guests_are_redirected_to_the_admin_login(): void
    {
        $response = $this->get('/admin');

        $response->assertRedirect(route('filament.admin.auth.login'));
    }

    public function test_the_admin_login_is_available(): void
    {
        $response = $this->get('/admin/login');

        $response->assertOk()->assertSee('Sign in');
    }
}
