import inertia from '@inertiajs/vite';
import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import laravel from 'laravel-vite-plugin';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vite-plus';

export default defineConfig({
    fmt: {
        singleQuote: true,
        tabWidth: 4,
        ignorePatterns: [
            'vendor/**',
            'public/**',
            'storage/**',
            '.agents/**',
            '.claude/**',
            '.grok/**',
            '.zed/**',
            '.codex/**',
            'AGENTS.md',
            'CLAUDE.md',
            '.mcp.json',
            'boost.json',
            'composer.lock',
            'package-lock.json',
        ],
    },
    lint: {
        ignorePatterns: ['vendor/**', 'public/**', 'storage/**'],
        options: {
            typeAware: true,
            typeCheck: true,
        },
    },
    plugins: [
        laravel({
            input: ['resources/js/app.tsx'],
            refresh: true,
        }),
        inertia(),
        react(),
        tailwindcss(),
    ],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./resources/js', import.meta.url)),
        },
    },
    server: {
        watch: {
            ignored: ['**/storage/framework/views/**'],
        },
    },
});
