import '../css/app.css';

import { createInertiaApp } from '@inertiajs/react';

void createInertiaApp({
    title: (title) => (title ? `${title} - Project PMP` : 'Project PMP'),
    strictMode: true,
});
