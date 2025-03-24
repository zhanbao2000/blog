document.addEventListener('DOMContentLoaded', function () {
    const STORAGE_KEY = 'blog_visitor_counter';
    const COUNTER_API = 'https://blog-counter.arisa.moe/api/addCount/arisa:blog';

    const trackVisit = () => {
        fetch(COUNTER_API, {
            method: 'GET',
            mode: 'cors'
        })
        .then(response => {
            if (response.ok) {
                localStorage.setItem(STORAGE_KEY,
                    JSON.stringify({
                        tracked: true,
                        expires: Date.now() + (7 * 24 * 60 * 60 * 1000)
                    })
                );
            }
        })
        .catch(console.error);
    };

    const storedData = localStorage.getItem(STORAGE_KEY);
    if (!storedData) {
        trackVisit();
    } else {
        const data = JSON.parse(storedData);
        if (data.expires < Date.now()) {
            localStorage.removeItem(STORAGE_KEY);
            trackVisit();
        }
    }
});
