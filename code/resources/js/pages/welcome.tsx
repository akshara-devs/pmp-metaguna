import { Head } from '@inertiajs/react';
import { useEffect, useState } from 'react';

import { Button } from '@/components/ui/button';

type WelcomeProps = {
    adminUrl: string;
};

export default function Welcome({ adminUrl }: WelcomeProps) {
    const [isDark, setIsDark] = useState(false);

    useEffect(() => {
        const savedIsDark = localStorage.getItem('theme') === 'dark';

        setIsDark(savedIsDark);
        document.documentElement.classList.toggle('dark', savedIsDark);
    }, []);

    function toggleTheme() {
        const nextIsDark = !isDark;

        setIsDark(nextIsDark);
        document.documentElement.classList.toggle('dark', nextIsDark);
        localStorage.setItem('theme', nextIsDark ? 'dark' : 'light');
    }

    return (
        <>
            <Head title="Welcome" />

            <div className="flex min-h-svh flex-col">
                <header className="flex items-center justify-between gap-4 border-b px-6 py-5 sm:px-12">
                    <span className="font-semibold">Project PMP</span>

                    <Button variant="outline" aria-pressed={isDark} onClick={toggleTheme}>
                        Dark theme
                    </Button>
                </header>

                <main className="flex flex-1 flex-col items-start justify-center gap-6 px-6 py-16 sm:px-12">
                    <p className="text-sm font-medium text-primary">Perpustakaan Merah Putih</p>
                    <h1 className="max-w-3xl text-4xl font-semibold tracking-tight sm:text-6xl">
                        Welcome to Project PMP.
                    </h1>
                    <p className="max-w-xl text-lg text-muted-foreground">
                        Open the admin panel to manage the library.
                    </p>

                    <Button asChild size="lg">
                        <a href={adminUrl}>Open admin panel</a>
                    </Button>
                </main>
            </div>
        </>
    );
}
