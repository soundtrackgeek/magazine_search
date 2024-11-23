// Configure marked to enable GitHub Flavored Markdown
marked.setOptions({
    gfm: true,
    breaks: true,
    headerIds: false,
    mangle: false,
    sanitize: false
});

function highlightText(text, query) {
    if (!query) return text;
    const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(escapedQuery, 'gi');
    return text.replace(regex, '<span class="highlight">$&</span>');
}

function renderMarkdownWithHighlight(markdown, query) {
    try {
        // First highlight the text in the markdown
        const highlightedMarkdown = highlightText(markdown, query);
        // Then render the markdown
        return marked.parse(highlightedMarkdown);
    } catch (error) {
        console.error('Error rendering markdown:', error);
        return markdown;
    }
}

let searchTimeout;
const searchInput = document.getElementById('search-input');
const resultsDiv = document.getElementById('results');
const loadingDiv = document.getElementById('loading');

searchInput.addEventListener('input', function() {
    const query = this.value.trim();
    const selectedMagazine = document.getElementById('magazine-filter').value;
    
    // Clear previous timeout
    clearTimeout(searchTimeout);
    
    // Show loading indicator
    loadingDiv.classList.remove('hidden');
    
    // Set new timeout
    searchTimeout = setTimeout(() => {
        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                magazine: selectedMagazine
            })
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading indicator
            loadingDiv.classList.add('hidden');
            
            // Clear previous results
            resultsDiv.innerHTML = '';
            
            if (data.results.length === 0) {
                resultsDiv.innerHTML = '<p class="text-center text-gray-500">No results found</p>';
                return;
            }
            
            // Display results
            data.results.forEach(result => {
                const resultElement = document.createElement('div');
                resultElement.className = 'search-result';
                
                const resultContent = `
                    <div class="search-result-title">
                        <h2 class="text-xl font-semibold">${result.magazine}</h2>
                        <p class="text-sm">Page ${result.page}</p>
                    </div>
                    <div class="result-container">
                        <div class="content-container">
                            <div class="markdown-body">
                                ${renderMarkdownWithHighlight(result.content, query)}
                            </div>
                        </div>
                        ${result.cover_image ? `
                            <div class="cover-image-container">
                                <img src="${result.cover_image}" alt="Magazine Cover" class="cover-image">
                            </div>
                        ` : ''}
                    </div>
                `;
                
                resultElement.innerHTML = resultContent;
                resultsDiv.appendChild(resultElement);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            loadingDiv.classList.add('hidden');
            resultsDiv.innerHTML = '<p class="text-center text-red-500">An error occurred while searching</p>';
        });
    }, 300);
});

document.getElementById('magazine-filter').addEventListener('change', function() {
    // Trigger search when magazine filter changes
    const event = new Event('input');
    searchInput.dispatchEvent(event);
});

// Theme handling
function getPreferredTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        return savedTheme;
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
}

// Initial theme setup
applyTheme(getPreferredTheme());

// Theme toggle handler
document.getElementById('theme-toggle').addEventListener('click', () => {
    const currentTheme = localStorage.getItem('theme') || getPreferredTheme();
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(newTheme);
});
