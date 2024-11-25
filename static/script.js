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

    // Check if the query is wrapped in quotes
    const isQuoted = /^".*"$/.test(query);
    
    if (isQuoted) {
        // For quoted searches, highlight the exact phrase (without the quotes)
        const phrase = query.slice(1, -1);  // Remove quotes
        const escapedPhrase = phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(escapedPhrase, 'gi');
        return text.replace(regex, '<span class="highlight">$&</span>');
    } else {
        // For regular searches, handle each term separately
        let highlightedText = text;
        
        // Split the query into terms, preserving quoted phrases
        const terms = query.match(/("[^"]+"|[^\s]+)/g) || [];
        
        // List of Elasticsearch operators and special syntax to ignore
        const operatorsToIgnore = [
            'AND', 'OR', 'NOT',  // Boolean operators
            '+', '-',            // Required/prohibited operators
            '(', ')',            // Grouping
            '*', '?',            // Wildcards
            '~', '^'             // Fuzzy and boost operators
        ];

        terms.forEach(term => {
            // Remove quotes if the term is quoted
            term = term.replace(/^"(.*)"$/, '$1');
            
            // Skip highlighting if the term is an operator
            if (operatorsToIgnore.includes(term.toUpperCase())) {
                return;
            }

            // Skip highlighting if the term starts with special characters
            if (/^[+\-~^()/]/.test(term)) {
                return;
            }

            const escapedTerm = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            const regex = new RegExp(escapedTerm, 'gi');
            highlightedText = highlightedText.replace(regex, '<span class="highlight">$&</span>');
        });
        
        return highlightedText;
    }
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
const resultsCountDiv = document.getElementById('results-count');
const paginationDiv = document.getElementById('pagination');
const prevPageBtn = document.getElementById('prev-page');
const nextPageBtn = document.getElementById('next-page');
const currentPageSpan = document.getElementById('current-page');
const totalPagesSpan = document.getElementById('total-pages');

let currentPage = 1;

function performSearch(query, selectedMagazine, page = 1) {
    // Show loading indicator
    loadingDiv.classList.remove('hidden');
    
    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query: query,
            magazine: selectedMagazine,
            page: page
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
            resultsCountDiv.classList.add('hidden');
            paginationDiv.classList.add('hidden');
            return;
        }
        
        // Display results count and pagination info
        resultsCountDiv.classList.remove('hidden');
        resultsCountDiv.textContent = `Found ${data.total_hits} result${data.total_hits === 1 ? '' : 's'}`;
        
        // Update pagination controls
        currentPage = data.current_page;
        currentPageSpan.textContent = currentPage;
        totalPagesSpan.textContent = data.total_pages;
        
        prevPageBtn.disabled = currentPage <= 1;
        nextPageBtn.disabled = currentPage >= data.total_pages;
        
        if (data.total_pages > 1) {
            paginationDiv.classList.remove('hidden');
        } else {
            paginationDiv.classList.add('hidden');
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

        // Scroll to top of results after loading new page
        resultsDiv.scrollIntoView({ behavior: 'smooth' });
    })
    .catch(error => {
        console.error('Error:', error);
        loadingDiv.classList.add('hidden');
        resultsDiv.innerHTML = '<p class="text-center text-red-500">An error occurred while searching</p>';
        paginationDiv.classList.add('hidden');
    });
}

searchInput.addEventListener('input', function() {
    const query = this.value.trim();
    const selectedMagazine = document.getElementById('magazine-filter').value;
    
    // Clear previous timeout
    clearTimeout(searchTimeout);
    
    // Reset to first page on new search
    currentPage = 1;
    
    // Set new timeout
    searchTimeout = setTimeout(() => {
        performSearch(query, selectedMagazine, currentPage);
    }, 300);
});

document.getElementById('magazine-filter').addEventListener('change', function() {
    // Reset to first page on filter change
    currentPage = 1;
    // Trigger search when magazine filter changes
    const event = new Event('input');
    searchInput.dispatchEvent(event);
});

// Pagination event listeners
prevPageBtn.addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        const query = searchInput.value.trim();
        const selectedMagazine = document.getElementById('magazine-filter').value;
        performSearch(query, selectedMagazine, currentPage);
    }
});

nextPageBtn.addEventListener('click', () => {
    const totalPages = parseInt(totalPagesSpan.textContent);
    if (currentPage < totalPages) {
        currentPage++;
        const query = searchInput.value.trim();
        const selectedMagazine = document.getElementById('magazine-filter').value;
        performSearch(query, selectedMagazine, currentPage);
    }
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
