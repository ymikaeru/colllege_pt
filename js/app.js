// ============================================
// STATE MANAGEMENT
// ============================================
let data = [];
let currentVolume = null;
let currentTheme = null;
let searchTerm = '';
let currentFontSize = localStorage.getItem('modalFontSize') || 'medium';
let currentLanguage = localStorage.getItem('appLanguage') || 'pt'; // 'pt' or 'jp'
let currentTitleData = null;
let searchTimeout = null;
let filterTranslatedOnly = false;

// ============================================
// DATA LOADING
// ============================================
async function loadData() {
    try {
        const response = await fetch('data/shin_college_data.json');
        data = await response.json();




        initializeApp();
    } catch (error) {
        console.error('Error loading data:', error);
        document.getElementById('loading').innerHTML = `
            <div style="text-align: center; color: var(--text-secondary);">
                <p style="font-size: 3rem; margin-bottom: 1rem;">⚠️</p>
                <p>Erro ao carregar dados</p>
                <p style="font-size: 0.9rem; margin-top: 0.5rem; color: var(--text-tertiary);">${error.message}</p>
            </div>
        `;
    }
}

// ============================================
// INITIALIZATION
// ============================================
function initializeApp() {
    updateGlobalLanguageUI();
    updateStatistics();
    showVolumes();
    setupEventListeners();
    hideLoading();
}

function setupEventListeners() {
    // Search
    document.getElementById('searchInput').addEventListener('input', handleSearch);

    // Back buttons
    document.getElementById('backToVolumes').addEventListener('click', showVolumes);
    document.getElementById('backToThemes').addEventListener('click', () => showThemes(currentVolume));

    // Modal close
    document.getElementById('closeModal').addEventListener('click', closeModal);
    document.getElementById('contentModal').addEventListener('click', (e) => {
        if (e.target.id === 'contentModal') closeModal();
    });

    // ESC key to close modal
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });

    // Font size controls
    document.getElementById('decreaseFontSize').addEventListener('click', () => changeFontSize('decrease'));
    document.getElementById('resetFontSize').addEventListener('click', () => changeFontSize('reset'));
    document.getElementById('increaseFontSize').addEventListener('click', () => changeFontSize('increase'));

    // Translation button (Modal)
    // document.getElementById('translationButton').addEventListener('click', toggleTranslation); // Deprecated/Replaced by global? 
    // Let's keep the modal button but make it trigger global toggle for now, or just hide it?
    // User wants a button on HOME. 
    // I will hook up the NEW button.
    const globalBtn = document.getElementById('globalLanguageBtn');
    if (globalBtn) {
        globalBtn.addEventListener('click', toggleGlobalLanguage);
    }
}

const uiTranslations = {
    'pt': {
        'volumesTitle': 'Selecione um Volume',
        'backToVolumes': '← Voltar aos Volumes',
        'backToThemes': '← Voltar aos Temas',
        'closeAllThemesBtn': { open: 'Abrir Todos', close: 'Fechar Todos' },
        'historyTitleText': 'Visto Recentemente',
        'clearHistoryBtn': 'Limpar Histórico',
        'labelThemes': 'Temas',
        'labelTopics': 'Tópicos',
        'labelDocs': 'Documentos',
        'loading': 'Carregando...',
        'breadcrumbVolumes': 'Volumes',
        'searchPlaceholder': 'Pesquisar por documentos, temas ou volumes...',
        'modalNavNext': 'Próximo',
        'modalNavPrev': 'Anterior',
        'modalNavClose': 'Fechar',
        'modalTOC': 'Tópicos',
        'siteTitle': 'Shin College'
    },
    'jp': {
        'volumesTitle': '巻を選択',
        'backToVolumes': '← 巻一覧に戻る',
        'backToThemes': '← テーマ一覧に戻る',
        'closeAllThemesBtn': { open: 'すべて開く', close: 'すべて閉じる' },
        'historyTitleText': '最近見た項目',
        'clearHistoryBtn': '履歴を消去',
        'labelThemes': 'テーマ',
        'labelTopics': 'トピック',
        'labelDocs': '文書',
        'loading': '読み込み中...',
        'breadcrumbVolumes': '巻一覧',
        'searchPlaceholder': '文書、テーマ、巻を検索...',
        'modalNavNext': '次へ',
        'modalNavPrev': '前へ',
        'modalNavClose': '閉じる',
        'modalTOC': '目次',
        'siteTitle': '新・カレッジ'
    }
};

// Volume Reversion Map (Since JSON has PT names in 'volume' field)
const volumeReverseMap = {
    "1. Seção de Busca do Caminho": "1.求道編",
    "2. Seção de Pontos Essenciais": "2.要義編",
    "3. Seção da Fé": "3.信仰編",
    "4. Outros": "4.その他",
    "5. Seção da Salvação": "5.救世編" // Assuming this exists or will exist
};

function getLocalizedVolume(ptName) {
    if (currentLanguage === 'jp') {
        return volumeReverseMap[ptName] || ptName;
    }
    return ptName;
}

function updateGlobalLanguageUI() {
    const btn = document.getElementById('globalLanguageBtn');
    if (btn) {
        btn.textContent = currentLanguage.toUpperCase();
    }

    const t = uiTranslations[currentLanguage];

    // Static Elements
    const setText = (id, text) => {
        const el = document.getElementById(id);
        if (el) el.textContent = text;
    };

    setText('volumesTitle', t.volumesTitle);
    setText('backToVolumes', t.backToVolumes); // Note: render functions might override this, handled there too?
    setText('backToThemes', t.backToThemes);
    setText('historyTitleText', t.historyTitleText);
    setText('clearHistoryBtn', t.clearHistoryBtn);
    setText('labelThemes', t.labelThemes);
    setText('labelTopics', t.labelTopics);
    setText('labelDocs', t.labelDocs);
    setText('loading', t.loading); // Wrapper content replacement? No, just p tag if p has id, but loading has p inside.

    // Loading text is inside #loading p. 
    const loadingEl = document.querySelector('#loading p');
    if (loadingEl) loadingEl.textContent = t.loading;

    // Site Title
    const siteLogo = document.getElementById('siteLogo');
    if (siteLogo) siteLogo.textContent = t.siteTitle;

    // Search Placeholder
    const searchInput = document.getElementById('searchInput');
    if (searchInput) searchInput.placeholder = t.searchPlaceholder;

    // Breadcrumb Root
    const breadcrumbRoot = document.querySelector('.breadcrumb-item[data-level="volumes"]');
    if (breadcrumbRoot) breadcrumbRoot.textContent = t.breadcrumbVolumes;

    // Modal Footer Tooltips
    const setTooltip = (id, text) => {
        const el = document.getElementById(id);
        if (el) el.title = text;
    }
    setTooltip('prevTitleBtn', t.modalNavPrev);
    setTooltip('nextTitleBtn', t.modalNavNext);
    setTooltip('closeModalFooterBtn', t.modalNavClose);

    // Toggle All Button text depends on state, handled in toggleAllThemes?
    // We should update it if it exists and we know state? 
    // Just force updateToggleAllButtonState if in themes view?
    updateToggleAllButtonState();
}

function toggleGlobalLanguage() {
    currentLanguage = currentLanguage === 'pt' ? 'jp' : 'pt';
    localStorage.setItem('appLanguage', currentLanguage);
    updateGlobalLanguageUI();

    // Re-render active view
    const modal = document.getElementById('contentModal');
    if (modal && !modal.classList.contains('hidden') && currentTitleData) {
        showContent(currentTitleData, false);
        return;
    }

    const titlesView = document.getElementById('titlesView');
    if (titlesView && !titlesView.classList.contains('hidden') && currentVolume !== null && currentTheme !== null) {
        showTitles(currentVolume, currentTheme);
        return;
    }

    const themesView = document.getElementById('themesView');
    if (themesView && !themesView.classList.contains('hidden') && currentVolume !== null) {
        showThemes(currentVolume);
        return;
    }

    // Default
    showVolumes();
}



// Helper for localization
function getLocalizedText(obj, fieldBase) {
    if (currentLanguage === 'pt') {
        return obj[fieldBase + '_ptbr'] || obj[fieldBase]; // Fallback to JP if empty
    } else {
        return obj[fieldBase]; // Original Japanese
    }
}

// ============================================
// STATISTICS
// ============================================
function updateStatistics(contextData = null) {
    let stats = {
        volumes: 0,
        themes: 0,
        titles: 0,
        articles: 0
    };
    const uniqueContent = new Set();
    const source = contextData || data;

    // Helper functions
    const processTitles = (titlesList) => {
        stats.titles += titlesList.length;
        titlesList.forEach(title => {
            title.publications.forEach(pub => {
                if (pub.content && pub.content.trim()) {
                    uniqueContent.add(pub.content.trim());
                }
            });
        });
    };

    const processThemes = (themesList) => {
        stats.themes += themesList.length;
        themesList.forEach(theme => processTitles(theme.titles));
    };

    // Determine data type and calculate
    if (Array.isArray(source)) {
        // Build-in detection for search results vs standard data
        if (source.length > 0 && source[0].matchType) {
            // Search Results
            const uniqueVolumes = new Set();
            const uniqueThemes = new Set();

            source.forEach(result => {
                uniqueVolumes.add(result.volume);
                uniqueThemes.add(`${result.volume}-${result.theme}`);

                // For titles/articles in search, we iterate the result items
                stats.titles++;
                result.title.publications.forEach(pub => {
                    if (pub.content && pub.content.trim()) {
                        uniqueContent.add(pub.content.trim());
                    }
                });
            });

            stats.volumes = uniqueVolumes.size;
            stats.themes = uniqueThemes.size;
        } else {
            // Global Data (Array of Volumes)
            stats.volumes = source.length;
            source.forEach(volume => processThemes(volume.themes));
        }
    } else if (source.themes) {
        // Single Volume
        stats.volumes = 0; // Don't show volumes count when viewing a single volume
        processThemes(source.themes);
    } else if (source.titles) {
        // Single Theme
        stats.volumes = 0; // Not aggregating volumes
        stats.themes = 0; // Don't show themes count when viewing a single theme
        processTitles(source.titles);
    }

    stats.articles = uniqueContent.size;


    animateCounter('totalThemes', stats.themes);
    animateCounter('totalTitles', stats.titles);
    animateCounter('totalArticles', stats.articles);
}

function animateCounter(elementId, target) {
    const element = document.getElementById(elementId);
    element.textContent = target;
}

// ============================================
// SEARCH FUNCTIONALITY
// ============================================
function handleSearch(e) {
    // Limpa o timeout anterior
    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }

    searchTerm = e.target.value.toLowerCase().trim();

    // Se o campo estiver vazio, volta para volumes imediatamente
    if (!searchTerm) {
        showVolumes();
        return;
    }

    // Requer mínimo de 2 caracteres antes de buscar
    if (searchTerm.length < 2) {
        return;
    }

    // Aguarda 500ms após o usuário parar de digitar
    searchTimeout = setTimeout(() => {
        const results = searchContent(searchTerm);
        displaySearchResults(results);
    }, 500);
}

function searchContent(term) {
    const results = [];
    const lowerTerm = term.toLowerCase();
    const keywords = lowerTerm.split(/\s+/).filter(k => k.length > 0);

    data.forEach(volume => {
        const volStr = (volume.volume || '') + ' ' + (volume.volume_ptbr || '');
        const volLower = volStr.toLowerCase();

        volume.themes.forEach(theme => {
            const themeStr = (theme.theme || '') + ' ' + (theme.theme_ptbr || '');
            const themeLower = themeStr.toLowerCase();

            theme.titles.forEach(title => {
                const titleStr = (title.title || '') + ' ' + (title.title_ptbr || '');
                const titleLower = titleStr.toLowerCase();

                if (title.publications) {
                    title.publications.forEach((pub, index) => {
                        // Combine text for context
                        // We include parent metadata so searching for "ThemeName Keyword" works
                        const pubContent = [
                            volLower,
                            themeLower,
                            titleLower,
                            (pub.publication_title || '').toLowerCase(),
                            (pub.publication_title_ptbr || '').toLowerCase(),
                            (pub.content || '').toLowerCase(),
                            (pub.content_ptbr || '').toLowerCase()
                        ].join(' ');

                        // Verify all keywords presence
                        if (keywords.every(keyword => pubContent.includes(keyword))) {
                            results.push({
                                volume: volume.volume,
                                theme: theme.theme,
                                title: title, // Parent title object
                                publication: pub, // Specific matched publication
                                pubIndex: index,
                                matchType: 'publication'
                            });
                        }
                    });
                }
            });
        });
    });

    return results;
}



function displayNoResults() {
    // Cria um overlay temporário com mensagem
    const overlay = document.createElement('div');
    overlay.className = 'search-no-results-overlay';
    overlay.innerHTML = `
        <div class="search-no-results-content">
            <p style="font-size: 3rem; margin-bottom: 1rem;">🔍</p>
            <p>Nenhum resultado encontrado</p>
            <p style="font-size: 0.9rem; color: var(--text-tertiary); margin-top: 0.5rem;">"${searchTerm}"</p>
        </div>
    `;

    document.body.appendChild(overlay);

    // Remove o overlay após 2 segundos
    setTimeout(() => {
        overlay.classList.add('fade-out');
        setTimeout(() => {
            document.body.removeChild(overlay);
        }, 300);
    }, 2000);

    // Limpa o input
    document.getElementById('searchInput').value = '';
}

function displaySearchResults(results) {
    hideAllViews();
    updateStatistics(results);
    const view = document.getElementById('titlesView');
    view.classList.remove('hidden');

    document.getElementById('themeTitle').textContent = `Resultados da pesquisa: "${searchTerm}"`;
    document.getElementById('backToThemes').style.display = 'none';

    const container = document.getElementById('titlesList');
    window.currentSearchResults = results;

    if (results.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 3rem; color: var(--text-tertiary);">
                <p style="font-size: 3rem; margin-bottom: 1rem;">🔍</p>
                <p>Nenhum resultado encontrado</p>
            </div>
        `;
        return;
    }

    container.innerHTML = results.map((result, index) => {
        // Display Logic for Publication Result
        const pub = result.publication;
        const displayTitle = (currentLanguage === 'pt' && pub.publication_title_ptbr) ? pub.publication_title_ptbr : (pub.publication_title || pub.header || 'Sem Título');

        // Context info (Parent Title)
        const parentTitle = (currentLanguage === 'pt' && result.title.title_ptbr) ? result.title.title_ptbr : result.title.title;

        return `
        <div class="title-item" onclick="openSearchResultByIndex(${index})">
            <div class="title-item-header">
                <div class="title-item-name" style="font-weight: 600;">${displayTitle}</div>
                <div class="title-item-badge" style="background:none; color:var(--text-tertiary); font-weight:normal; font-size: 0.85rem; padding:0;">
                    ${parentTitle}
                </div>
            </div>
            <!-- Optional: Show snippet? For now just title is requested -->
        </div>
    `}).join('');

    updateBreadcrumb([
        { text: 'Volumes', action: () => { document.getElementById('searchInput').value = ''; showVolumes(); } },
        { text: `Pesquisa: "${searchTerm}"`, active: true }
    ]);
}

function openSearchResultByIndex(index) {
    if (window.currentSearchResults && window.currentSearchResults[index]) {
        const result = window.currentSearchResults[index];

        // Find volume and theme indices maps
        const volumeIndex = data.findIndex(v => v.volume === result.volume);
        const volumeObj = volumeIndex >= 0 ? data[volumeIndex] : null;

        let themeIndex = -1;
        let themeName = result.theme;

        if (volumeObj) {
            themeIndex = volumeObj.themes.findIndex(t => t.theme === result.theme);
            if (themeIndex >= 0) {
                themeName = volumeObj.themes[themeIndex].theme_ptbr || volumeObj.themes[themeIndex].theme;
            }
        }

        // Inject path info
        const titleWithContext = {
            ...result.title,
            pathInfo: {
                volume: volumeObj ? (volumeObj.volume_ptbr || formatVolumeName(volumeObj.volume)) : formatVolumeName(result.volume),
                theme: themeName,
                volumeIndex: volumeIndex,
                themeIndex: themeIndex
            }
        };

        // Pass scrollToId to showContent. We use 'pub-INDEX' format from showContent generation
        const targetId = `pub-${result.pubIndex}`;
        showContent(titleWithContext, true, targetId);
    }
}

// ============================================
// NAVIGATION VIEWS
// ============================================
function showVolumes() {
    hideAllViews();
    currentVolume = null;
    currentTheme = null;
    document.getElementById('searchInput').value = '';
    searchTerm = '';

    const view = document.getElementById('volumesView');
    view.classList.remove('hidden');

    // Show statistics only on home page
    document.getElementById('statsFooter').style.display = 'block';

    const container = document.getElementById('volumesList');
    updateStatistics(); // Reset to global stats

    // ------------------------------------------
    // MODE 1: SHOW TRANSLATED ONLY (FILTER ACTIVE)
    // ------------------------------------------


    // ------------------------------------------
    // MODE 2: NORMAL VIEW (SHOW ALL VOLUMES + VIRTUAL CARD)
    // ------------------------------------------
    let html = data.map((volume, index) => {
        const themeCount = volume.themes.length;
        let titleCount = 0;
        volume.themes.forEach(theme => titleCount += theme.titles.length);

        // Use localized volume name (Reverting PT -> JP if needed)
        const displayVol = getLocalizedVolume(volume.volume);

        const t = uiTranslations[currentLanguage];
        const labelThemes = t.labelThemes;
        const labelTopics = t.labelTopics;

        return `
            <div class="card" onclick="showThemes(${index})">
                <div class="card-title">${displayVol}</div>
                <div class="card-subtitle">
                    ${themeCount} ${labelThemes} · ${titleCount} ${labelTopics}
                </div>
            </div>
        `;
    }).join('');

    // Append Virtual Volume Card for Translations


    container.innerHTML = html;
    updateBreadcrumb([{ text: uiTranslations[currentLanguage].breadcrumbVolumes, active: true }]);
}

function enterTranslatedFilter() {
    filterTranslatedOnly = true;
    const translatedTree = getTranslatedContentTree();

    hideAllViews();

    // Custom view for translated content reusable components
    const view = document.getElementById('titlesView');
    view.classList.remove('hidden');
    document.getElementById('backToThemes').style.display = 'none';

    // Update stats logic to show nothing or custom stats? 
    // updateStatistics can handle context data if we flatten it, but for categorized view maybe just hide stats or show total translated count.
    // For now, let's just update the list.

    const container = document.getElementById('titlesList');

    if (translatedTree.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 3rem; color: var(--text-tertiary);">
                <p style="font-size: 3rem; margin-bottom: 1rem;">🌐</p>
                <p>Nenhum conteúdo traduzido encontrado</p>
            </div>
        `;
    } else {
        container.innerHTML = renderTranslatedTree(translatedTree);
    }

    document.getElementById('themeTitle').textContent = `Ensinamentos Traduzidos`;

    updateBreadcrumb([
        { text: 'Volumes', action: exitTranslatedFilter },
        { text: 'Ensinamentos Traduzidos', active: true }
    ]);
}

function getTranslatedContentTree() {
    const tree = [];

    data.forEach(volume => {
        const translatedThemes = [];

        volume.themes.forEach(theme => {
            const translatedTitles = [];

            theme.titles.forEach(title => {
                if (isFullyTranslated(title)) {
                    translatedTitles.push(title);
                }
            });

            if (translatedTitles.length > 0) {
                translatedThemes.push({
                    originalTheme: theme,
                    titles: translatedTitles
                });
            }
        });

        if (translatedThemes.length > 0) {
            tree.push({
                originalVolume: volume,
                themes: translatedThemes
            });
        }
    });

    return tree;
}

function renderTranslatedTree(tree) {
    return tree.map(volObj => `
        <div class="translated-volume-group" style="margin-bottom: 2rem;">
            <div style="font-size: 1.2rem; font-weight: bold; color: var(--primary); margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid var(--border-color);">
                ${volObj.originalVolume.volume_ptbr || formatVolumeName(volObj.originalVolume.volume)}
            </div>
            ${volObj.themes.map(themeObj => `
                <div class="translated-theme-group" style="margin-left: 1rem; margin-bottom: 1.5rem;">
                    <div style="font-size: 1rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 0.8rem;">
                        ${themeObj.originalTheme.theme_ptbr || themeObj.originalTheme.theme}
                    </div>
                    ${renderTitlesList(themeObj.titles, volObj.originalVolume, themeObj.originalTheme)}
                </div>
            `).join('')}
        </div>
    `).join('');
}

function renderTitlesList(titles, volume, theme) {
    return titles.map(title => {
        const displayTitle = title.title_ptbr || title.title;

        // Find indices for opening content
        // This is a bit inefficient to do repeatedly, but data size is manageable.
        const volIndex = data.indexOf(volume);
        const themeIndex = volume.themes.indexOf(theme);
        const titleIndex = theme.titles.indexOf(title);

        return `
        <div class="title-item" onclick="openContentFromPath(${volIndex}, ${themeIndex}, ${titleIndex})" style="border-left: 3px solid var(--primary-light);">
            <div class="title-item-header">
                <div class="title-item-name">${displayTitle}</div>
                <div class="title-item-badge">${title.publications.length} Documentos</div>
            </div>
        </div>
        `;
    }).join('');
}

function openContentFromPath(volIdx, themeIdx, titleIdx) {
    if (volIdx >= 0 && themeIdx >= 0 && titleIdx >= 0) {
        const volume = data[volIdx];
        const theme = volume.themes[themeIdx];
        const title = theme.titles[titleIdx];

        const titleWithContext = {
            ...title,
            pathInfo: {
                volume: volume.volume_ptbr || formatVolumeName(volume.volume),
                theme: theme.theme_ptbr || theme.theme,
                volumeIndex: volIdx,
                themeIndex: themeIdx
            }
        };
        showContent(titleWithContext);
    }
}

// Strict check: Title is considered translated ONLY if ALL publications have translated content
function isFullyTranslated(title) {
    if (!title.publications || title.publications.length === 0) return false;
    return title.publications.every(pub => pub.content_ptbr && pub.content_ptbr.trim().length > 0);
}

// Loose check: Returns true if AT LEAST ONE publication has translated content
function hasAnyTranslation(title) {
    if (!title.publications || title.publications.length === 0) return false;
    return title.publications.some(pub => pub.content_ptbr && pub.content_ptbr.trim().length > 0);
}

// Helper to get the best display title (PT fallback to JP)
function getDisplayTitle(title) {
    if (hasAnyTranslation(title)) {
        if (title.title_ptbr) return title.title_ptbr;
        // Fallback: try to find first publication with a PT title
        const pubWithTitle = title.publications.find(p => p.publication_title_ptbr);
        if (pubWithTitle) return pubWithTitle.publication_title_ptbr;
    }
    return title.title;
}

function exitTranslatedFilter() {
    filterTranslatedOnly = false;
    // Clear search if it was active, though this function is for breadcrumb
    document.getElementById('searchInput').value = '';
    showVolumes();
}

function hasVolumeTranslation(volume) {
    return volume.themes.some(theme => hasThemeTranslation(theme));
}

function hasThemeTranslation(theme) {
    // Check if theme has explicit PT title OR has any translated content
    // Note: Most themes have theme_ptbr generated, so relying on that might be too broad 
    // if the content isn't actually translated.
    // Better to check for actual translated content in publications OR explicitly marked translated titles.

    // Check if any title has translation
    return theme.titles.some(title => {
        // Title has PT translation?
        if (title.title_ptbr && title.title_ptbr !== title.title) return true;

        // Publications have content_ptbr?
        return title.publications.some(pub => pub.content_ptbr && pub.content_ptbr.trim().length > 0);
    });
}

function showThemes(volumeIndex) {
    hideAllViews();
    currentVolume = volumeIndex;
    const volume = data[volumeIndex];

    const view = document.getElementById('themesView');
    view.classList.remove('hidden');

    // Hide statistics on themes view
    document.getElementById('statsFooter').style.display = 'none';

    // Update Header
    const displayVol = getLocalizedVolume(volume.volume);
    document.getElementById('volumeTitle').textContent = displayVol;
    document.getElementById('backToThemes').style.display = 'none';
    document.getElementById('backToVolumes').style.display = 'inline-flex';
    document.getElementById('backToVolumes').textContent = uiTranslations[currentLanguage].backToVolumes;

    // Ocultar botão de toggle já que não há mais accordion
    const toggleBtn = document.getElementById('closeAllThemesBtn');
    if (toggleBtn) toggleBtn.style.display = 'none';

    const container = document.getElementById('themesList');

    // Filter themes if needed
    let displayThemes = volume.themes;
    if (filterTranslatedOnly) {
        displayThemes = volume.themes.filter(theme => hasThemeTranslation(theme));
    }

    if (displayThemes.length === 0 && filterTranslatedOnly) {
        container.innerHTML = `
            <div style="text-align: center; padding: 3rem; color: var(--text-tertiary); grid-column: 1/-1;">
                <p style="font-size: 3rem; margin-bottom: 1rem;">🌐</p>
                <p>${currentLanguage === 'pt' ? 'Nenhum tema traduzido neste volume' : '翻訳されたテーマはありません'}</p>
            </div>
        `;
        return;
    }

    container.innerHTML = displayThemes.map((theme, _) => {
        // Find original index
        const themeIndex = volume.themes.indexOf(theme);

        // Filtrar títulos válidos
        const validTitles = filterValidTitles(theme.titles);
        const groupedTitles = groupNumberedTitles(validTitles);

        // Renderizar títulos diretamente
        const titlesHTML = groupedTitles.map((title, index) => {
            if (title.title === '---') {
                return `<div class="separator-item"></div>`;
            }

            const displayTitle = getLocalizedText(title, 'title');
            const labelDocs = currentLanguage === 'pt' ? 'Documentos' : '文書';

            return `
            <div class="title-item" onclick="event.stopPropagation(); showContentFromAccordion('${title.title.replace(/'/g, "\\'")}')">
                <div class="title-item-header">
                    <div class="title-item-name">${displayTitle}</div>
                    <div class="title-item-badge">${title.publications.length} ${labelDocs}</div>
                </div>
            </div>
            `;
        }).join('');

        const displayTheme = getLocalizedText(theme, 'theme');
        const labelTopics = currentLanguage === 'pt' ? 'Tópicos' : 'トピック';

        return `
            <div id="theme-card-${themeIndex}" class="card">
                <div class="card-header-content">
                    <div class="card-info">
                        <div class="card-title">${displayTheme}</div>
                        <div class="card-subtitle">
                            ${groupedTitles.filter(t => t.title !== '---').length} ${labelTopics}
                        </div>
                    </div>
                </div>
                <div id="theme-titles-${themeIndex}" class="titles-container">${titlesHTML}</div>
            </div>
        `;
    }).join('');

    updateBreadcrumb([
        { text: uiTranslations[currentLanguage].breadcrumbVolumes, action: showVolumes },
        { text: displayVol, active: true }
    ]);
}

function toggleTheme(volumeIndex, themeIndex) {
    const card = document.getElementById(`theme-card-${themeIndex}`);
    const container = document.getElementById(`theme-titles-${themeIndex}`);
    const volume = data[volumeIndex];
    const theme = volume.themes[themeIndex];

    const isExpanded = card.classList.contains('expanded');

    if (isExpanded) {
        card.classList.remove('expanded');
    } else {
        if (container.innerHTML.trim() === '') {
            renderTitlesInTheme(container, theme.titles);
        }

        // Only expand if there is content to show
        if (container.children.length > 0) {
            card.classList.add('expanded');
        } else {
            console.log('No visible titles for this theme');
        }
    }
    updateToggleAllButtonState();
}

function toggleAllThemes() {
    const container = document.getElementById('themesList');
    if (!container) return;
    const cards = container.querySelectorAll('.card');
    const btn = document.getElementById('closeAllThemesBtn');

    const anyExpanded = Array.from(cards).some(card => card.classList.contains('expanded'));

    if (anyExpanded) {
        // Close all
        cards.forEach(card => card.classList.remove('expanded'));
        const t = uiTranslations[currentLanguage];
        btn.textContent = t.closeAllThemesBtn.open;
    } else {
        // Open all
        const volume = data[data.findIndex(v => v.volume === document.getElementById('volumeTitle').textContent)] || data[currentVolume];

        cards.forEach((card, index) => {
            const titlesContainer = card.querySelector('.titles-container');

            // Render content if needed
            if (titlesContainer && titlesContainer.innerHTML.trim() === '') {
                // Determine index match. themesList maps directly to volume.themes
                const theme = volume.themes[index];
                renderTitlesInTheme(titlesContainer, theme.titles);
            }

            // Only expand if not empty
            if (titlesContainer && titlesContainer.children.length > 0) {
                card.classList.add('expanded');
            }
        });
        const t = uiTranslations[currentLanguage];
        btn.textContent = t.closeAllThemesBtn.close;
    }
}

function updateToggleAllButtonState() {
    const container = document.getElementById('themesList');
    if (!container) return;
    const cards = container.querySelectorAll('.card');
    const btn = document.getElementById('closeAllThemesBtn');

    const anyExpanded = Array.from(cards).some(card => card.classList.contains('expanded'));

    const t = uiTranslations[currentLanguage];
    if (anyExpanded) {
        btn.textContent = t.closeAllThemesBtn.close;
    } else {
        btn.textContent = t.closeAllThemesBtn.open;
    }
}


function filterValidTitles(titles) {
    // 1. Filtrar títulos sem publicações (mantendo separadores por enquanto)
    const filtered = titles.filter(title =>
        title.title === '---' || (title.publications && title.publications.length > 0)
    );

    // 2. Verificar se restou algum título real (não-separador)
    const hasRealContent = filtered.some(title => title.title !== '---');

    // Se só tem separadores, retorna vazio para evitar renderizar apenas linhas
    if (!hasRealContent) {
        return [];
    }

    return filtered;
}

function renderTitlesInTheme(container, titles) {
    // Filtrar títulos vazios e separadores órfãos
    let titlesWithContent = filterValidTitles(titles);

    // Apply translation filter if active
    if (filterTranslatedOnly) {
        titlesWithContent = titlesWithContent.filter(title => {
            // Keep separators to maintain structure? Or remove?
            // Removing separators might break visual grouping, but separators aren't "translated".
            // Let's keep separator if we are filtering? No, usually filters remove non-matches.
            if (title.title === '---') return false;

            // Check for translation
            return isFullyTranslated(title);
        });
    }

    const groupedTitles = groupNumberedTitles(titlesWithContent);

    if (groupedTitles.length === 0) {
        container.innerHTML = `<div style="padding:10px; color:var(--text-tertiary); font-style:italic;">Nenhum tópico traduzido</div>`;
        return;
    }

    container.innerHTML = groupedTitles.map((title, index) => {
        if (title.title === '---') {
            return `<div class="separator-item"></div>`;
        }

        const displayTitle = getDisplayTitle(title);

        return `
        <div class="title-item" onclick="event.stopPropagation(); showContentFromAccordion('${title.title.replace(/'/g, "\\'")}')">
            <div class="title-item-header">
                <div class="title-item-name">${displayTitle}</div>
                <div class="title-item-badge">${title.publications.length} Documentos</div>
            </div>
        </div>
    `}).join('');
}

function showContentFromAccordion(titleString) {
    if (currentVolume === null) {
        return;
    }
    const volume = data[currentVolume];

    for (let t = 0; t < volume.themes.length; t++) {
        const theme = volume.themes[t];
        const grouped = groupNumberedTitles(theme.titles);
        const found = grouped.find(g => g.title === titleString);

        if (found) {
            // Fix for navigation arrows: Set the current context
            window.currentGroupedTitles = grouped;

            const titleWithContext = {
                ...found,
                pathInfo: {
                    volume: volume.volume_ptbr || formatVolumeName(volume.volume),
                    theme: theme.theme_ptbr || theme.theme,
                    volumeIndex: currentVolume,
                    themeIndex: t
                }
            };
            showContent(titleWithContext);
            return;
        }
    }
}


function showTitles(volumeIndex, themeIndex) {
    hideAllViews();
    currentVolume = volumeIndex;
    currentTheme = themeIndex;

    const volume = data[volumeIndex];
    const theme = volume.themes[themeIndex];

    const view = document.getElementById('titlesView');
    view.classList.remove('hidden');

    // Hide statistics on titles view
    document.getElementById('statsFooter').style.display = 'none';

    // Filtra títulos vazios e separadores órfãos, depois agrupa
    let titlesWithContent = filterValidTitles(theme.titles);

    // Apply translation filter if active
    if (filterTranslatedOnly) {
        titlesWithContent = titlesWithContent.filter(title => {
            if (title.title === '---') return false;
            return isFullyTranslated(title);
        });
    }

    const groupedTitles = groupNumberedTitles(titlesWithContent);
    window.currentGroupedTitles = groupedTitles;

    document.getElementById('themeTitle').textContent = theme.theme_ptbr || theme.theme;
    document.getElementById('backToThemes').style.display = 'inline-flex';

    const container = document.getElementById('titlesList');
    container.innerHTML = groupedTitles.map((title, index) => {
        if (title.title === '---') {
            return `<div class="separator-item"></div>`;
        }
        const displayTitle = getDisplayTitle(title);
        return `
        <div class="title-item" onclick="openContentByIndex(${index})">
            <div class="title-item-header">
                <div class="title-item-name">${displayTitle}</div>
                <div class="title-item-badge">${title.publications.length} Documentos</div>
            </div>
        </div>
    `}).join('');

    updateBreadcrumb([
        { text: 'Volumes', action: showVolumes },
        { text: volume.volume_ptbr || formatVolumeName(volume.volume), action: () => showThemes(volumeIndex) },
        { text: theme.theme_ptbr || theme.theme, active: true }
    ]);
}

function openContentByIndex(index) {
    if (window.currentGroupedTitles && window.currentGroupedTitles[index]) {
        const titleData = window.currentGroupedTitles[index];

        // Inject path info if missing and we have context
        if (!titleData.pathInfo && typeof currentVolume === 'number' && typeof currentTheme === 'number') {
            const vol = data[currentVolume];
            const thm = vol ? vol.themes[currentTheme] : null;
            if (vol && thm) {
                titleData.pathInfo = {
                    volume: vol.volume_ptbr || formatVolumeName(vol.volume),
                    theme: thm.theme_ptbr || thm.theme,
                    volumeIndex: currentVolume,
                    themeIndex: currentTheme
                };
            }
        }

        showContent(titleData);
    }
}

// ============================================
// MODAL CONTENT
// ============================================
function showContent(title, isInitialLoad = true, scrollToId = null) {
    const modal = document.getElementById('contentModal');
    // First, filter out empty content (must have valid content in at least one language)
    const basePubs = title.publications
        .filter(pub => (pub.content && pub.content.trim()) || (pub.content_ptbr && pub.content_ptbr.trim()));

    // Check availability
    const hasTranslation = basePubs.some(pub => pub.content_ptbr && pub.content_ptbr.trim());

    const showPT = currentLanguage === 'pt';

    // Store current title data
    currentTitleData = title;

    // Update Modal Title
    const displayTitle = getLocalizedText(title, 'title');
    document.getElementById('modalTitle').textContent = displayTitle;

    // Processa os dados para navegação e conteúdo
    const processedPubs = basePubs.map((pub, index) => ({
        ...pub,
        id: `pub-${index}`,
        displayTitle: (showPT && pub.publication_title_ptbr) ? pub.publication_title_ptbr : (pub.publication_title || pub.header || (pub.type === 'intro' ? 'Introdução' : 'Sem Título'))
    }));

    // ... translation button logic skipped, assuming it remains similar or you can copy it back ...
    // Wait, I am replacing a huge chunk. I should keep the translation button logic.
    // I will use ... skipping ... in my mind but I must provide full replacement for the range.

    // ... Translation Button Logic ...
    const translationButton = document.getElementById('translationButton');
    if (hasTranslation) {
        translationButton.classList.remove('hidden');
        translationButton.textContent = showPT ? "Original" : "PT";
        if (showPT) {
            translationButton.classList.add('active');
        } else {
            translationButton.classList.remove('active');
        }
        translationButton.onclick = toggleGlobalLanguage;
    } else {
        translationButton.classList.add('hidden');
    }

    // Conta ocorrências de cada título para numerar duplicatas
    const titleCounts = {};
    processedPubs.forEach(pub => {
        titleCounts[pub.displayTitle] = (titleCounts[pub.displayTitle] || 0) + 1;
    });

    const currentCounts = {};
    const navigationItems = processedPubs.map(pub => {
        let label = pub.displayTitle;
        if (titleCounts[pub.displayTitle] > 1) {
            currentCounts[pub.displayTitle] = (currentCounts[pub.displayTitle] || 0) + 1;
            label = `${pub.displayTitle} ${currentCounts[pub.displayTitle]}`;
        }
        return { ...pub, label };
    });

    // Gera o HTML da navegação
    let navHTML = '';
    if (navigationItems.length > 1) {
        const tocLabel = currentLanguage === 'pt' ? 'Tópicos' : '目次';
        navHTML = `
            <div class="modal-nav-container">
                <button class="modal-nav-toggle" onclick="toggleModalNav(this)">
                    <span>${tocLabel} (${navigationItems.length})</span>
                    <span class="chevron">▼</span>
                </button>
                <div class="modal-nav-content" id="modalNavContent">
                    <div class="modal-nav">
                        ${navigationItems.map(item => `
                            <button class="modal-nav-item" onclick="document.getElementById('${item.id}').scrollIntoView({ behavior: 'smooth' })">
                                ${parseMarkdown(item.label)}
                            </button>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    // Metadados - Caminho do conteúdo
    const metaContainer = document.getElementById('modalMeta');
    if (title.pathInfo) {
        const titleStringEscaped = title.title.replace(/'/g, "\\'");
        metaContainer.innerHTML = `
            <div class="modal-meta-item modal-meta-link" onclick="closeModalAndNavigate('volume', ${title.pathInfo.volumeIndex})">${title.pathInfo.volume}</div>
            <div class="modal-meta-item">→</div>
            <div class="modal-meta-item modal-meta-link" onclick="closeModalAndNavigate('theme', ${title.pathInfo.volumeIndex}, ${title.pathInfo.themeIndex}, '${titleStringEscaped}')">${title.pathInfo.theme}</div>
        `;
    } else {
        metaContainer.innerHTML = '';
    }

    // Save to history
    saveHistory(title);

    // Gera o HTML do conteúdo
    const publicationsHTML = navigationItems.map(pub => {
        const contentToShow = (showPT && pub.content_ptbr) ? pub.content_ptbr : pub.content;
        const noContentMsg = currentLanguage === 'pt' ? 'Conteúdo não disponível' : 'コンテンツなし';

        return `
        <div id="${pub.id}" class="publication">
            <div class="publication-header">${parseMarkdown(pub.displayTitle)}</div>
            <div class="publication-content">${parseMarkdown(contentToShow || noContentMsg)}</div>
        </div>
    `}).join('');

    document.getElementById('modalBody').innerHTML = navHTML + publicationsHTML;

    // Apply font size
    applyFontSize();

    // Update Footer Navigation
    updateModalFooter(title);

    // Reset scroll position
    const modalContent = modal.querySelector('.modal-content');
    if (modalContent) modalContent.scrollTop = 0;
    const scrollableArea = modal.querySelector('.modal-scrollable-area');
    if (scrollableArea) scrollableArea.scrollTop = 0;

    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';

    // Scroll to specific element if requested
    if (scrollToId) {
        setTimeout(() => {
            const target = document.getElementById(scrollToId);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                // Optional: flash highlight
                target.classList.add('search-highlight');
                setTimeout(() => target.classList.remove('search-highlight'), 2000);
            }
        }, 300); // Slight delay to ensure render and transition
    }
}

function toggleModalNav(btn) {
    const content = document.getElementById('modalNavContent');
    if (content.style.maxHeight) {
        content.style.maxHeight = null;
        content.classList.remove('open');
        btn.classList.remove('active');
    } else {
        content.classList.add('open');
        content.style.maxHeight = content.scrollHeight + "px";
        btn.classList.add('active');
    }
}

function parseMarkdown(text) {
    if (!text) return '';

    // Bold: **text** or ＊＊text＊＊
    // Handles optional whitespace inside the bold tags
    let html = text.replace(/(?:\*\*|＊＊)\s*(.*?)\s*(?:\*\*|＊＊)/g, '<strong>$1</strong>');

    // Italic: *text* or ＊text＊
    html = html.replace(/(?:\*|＊)\s*(.*?)\s*(?:\*|＊)/g, '<em>$1</em>');

    return html;
}



function closeModal() {
    document.getElementById('contentModal').classList.add('hidden');
    document.body.style.overflow = '';
    // Hide footer when modal closes
    const footer = document.getElementById('modalNavFooter');
    if (footer) footer.classList.add('hidden');
}

// ============================================
// BREADCRUMB
// ============================================
// ============================================
// BREADCRUMB
// ============================================
function updateBreadcrumb(items) {
    const breadcrumb = document.getElementById('breadcrumb');
    window.breadcrumbActions = []; // Reset actions

    breadcrumb.innerHTML = items.map((item, index) => {
        if (item.action) {
            window.breadcrumbActions[index] = item.action;
        }

        return `
            <span class="breadcrumb-item ${item.active ? 'active' : ''}" 
                  ${item.action ? `onclick="window.breadcrumbActions[${index}]()"` : ''}>
                ${item.text}
            </span>
        `;
    }).join('');
}

// ============================================
// UTILITY FUNCTIONS
// ============================================
function hideAllViews() {
    document.getElementById('volumesView').classList.add('hidden');
    document.getElementById('themesView').classList.add('hidden');
    document.getElementById('titlesView').classList.add('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

function formatVolumeName(name) {
    // Remove volume number prefix for cleaner display
    return name.replace(/^\d+\./, '').trim();
}

function extractThemeNumber(themeName) {
    // Extracts number from "1 - Theme Name" or "10. Theme Name"
    const match = themeName.match(/^(\d+)[-.\s]/);
    return match ? parseInt(match[1], 10) : null;
}

function groupNumberedTitles(titles) {
    const grouped = new Map();

    titles.forEach((title, index) => {
        // Skip empty titles (without publications) and separators
        if (title.title === '---' || !title.publications || title.publications.length === 0) {
            return;
        }

        // Remove números do final do título (suporta 1, 2, ３, ４, (1), （１）, - 1, etc.)
        const baseTitle = title.title.replace(/[　\s]*([-\u2010-\u2015]|\(|（)?[　\s]*[0-9０-９１-９]+[　\s]*(\)|）)?[　\s]*$/, '').trim();

        // Handle Portuguese title if present
        let baseTitlePt = null;
        if (title.title_ptbr) {
            // Strip western numbers from end of PT string, handling (1), - 1 etc
            baseTitlePt = title.title_ptbr.replace(/[　\s]*([-]|\()?[　\s]*[0-9]+[　\s]*(\))?[　\s]*$/, '').trim();
        }

        if (grouped.has(baseTitle)) {
            // Adiciona publicações ao título existente
            grouped.get(baseTitle).publications.push(...title.publications);
        } else {
            // Cria nova entrada com o título base
            grouped.set(baseTitle, {
                title: baseTitle,
                title_ptbr: baseTitlePt,
                publications: [...title.publications]
            });
        }
    });

    return Array.from(grouped.values());
}

// ============================================
// FONT SIZE CONTROL
// ============================================
function changeFontSize(action) {
    const sizes = ['small', 'medium', 'large', 'x-large'];
    const currentIndex = sizes.indexOf(currentFontSize);

    if (action === 'decrease' && currentIndex > 0) {
        currentFontSize = sizes[currentIndex - 1];
    } else if (action === 'increase' && currentIndex < sizes.length - 1) {
        currentFontSize = sizes[currentIndex + 1];
    } else if (action === 'reset') {
        currentFontSize = 'medium';
    }

    localStorage.setItem('modalFontSize', currentFontSize);
    applyFontSize();
}

function applyFontSize() {
    const modalBody = document.getElementById('modalBody');
    const fontSizes = {
        'small': '0.9rem',
        'medium': '1rem',
        'large': '1.1rem',
        'x-large': '1.2rem'
    };

    if (modalBody) {
        modalBody.style.fontSize = fontSizes[currentFontSize] || fontSizes['medium'];
    }
}

// ============================================
// MODAL NAVIGATION HELPERS
// ============================================
// ============================================
// MODAL NAVIGATION HELPERS
// ============================================
function closeModalAndNavigate(type, volumeIndex, themeIndex, targetTitle = null) {
    closeModal();

    if (type === 'volume' && volumeIndex >= 0) {
        showThemes(volumeIndex);
    } else if (type === 'theme' && volumeIndex >= 0 && themeIndex >= 0) {
        if (targetTitle) {
            navigateToAndHighlight(volumeIndex, themeIndex, targetTitle);
        } else {
            showTitles(volumeIndex, themeIndex);
        }
    }
}

function navigateToAndHighlight(volumeIndex, themeIndex, titleString) {
    // Navega para a view de temas
    showThemes(volumeIndex);

    // Normalize title to match grouped view (remove trailing numbers)
    // Matches the logic in groupNumberedTitles
    const normalizedTarget = titleString.replace(/[　\s]*[0-9０-９１-９]+\s*$/, '').trim();

    // Aguarda um momento para a view renderizar
    setTimeout(() => {
        // Expande o card do tema
        const card = document.getElementById(`theme-card-${themeIndex}`);
        const container = document.getElementById(`theme-titles-${themeIndex}`);
        const volume = data[volumeIndex];
        const theme = volume.themes[themeIndex];

        if (card && !card.classList.contains('expanded')) {
            card.classList.add('expanded');
            if (container.innerHTML.trim() === '') {
                renderTitlesInTheme(container, theme.titles);
            }
        }

        // Aguarda a renderização dos títulos
        setTimeout(() => {
            // Encontra o elemento do título dentro do container
            const titleItems = container.querySelectorAll('.title-item-name');
            let targetElement = null;

            titleItems.forEach(item => {
                // Determine equality based on normalized text
                if (item.textContent.trim() === normalizedTarget) {
                    targetElement = item.closest('.title-item');
                }
            });

            if (targetElement) {
                // Scroll suave até o elemento
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });

                // Adiciona classe de highlight
                targetElement.classList.add('search-highlight');

                // Remove o highlight após 3 segundos
                setTimeout(() => {
                    targetElement.classList.remove('search-highlight');
                }, 3000);
            }
        }, 300);
    }, 100);
}

// ============================================
// TRANSLATION TOGGLE
// ============================================
// function toggleTranslation() { ... } // Replaced by toggleGlobalLanguage 
// We can remove it or leave it as a no-op if referenced elsewhere (checked listeners, simplified).


// ============================================
// SCROLL TO TOP
// ============================================
function setupScrollToTop() {
    const goToTopBtn = document.getElementById('goToTopBtn');

    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            goToTopBtn.classList.add('visible');
        } else {
            goToTopBtn.classList.remove('visible');
        }
    });

    goToTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// ============================================
// MOBILE FOOTER NAVIGATION
// ============================================
let currentNavContext = { list: null, index: -1 };
let footerHideTimeout;

function updateModalFooter(titleData) {
    const footer = document.getElementById('modalNavFooter');
    if (!footer) return;

    // Determine context
    currentNavContext.list = null;

    // Check if in current grouped titles (Theme)
    if (window.currentGroupedTitles && window.currentGroupedTitles.some(t => t.title === titleData.title)) {
        currentNavContext.list = window.currentGroupedTitles;
    }
    // Check if in search results
    else if (window.currentSearchResults && window.currentSearchResults.some(r => r.title.title === titleData.title)) {
        currentNavContext.list = window.currentSearchResults.map(r => r.title);
    }

    // Find index
    if (currentNavContext.list) {
        currentNavContext.index = currentNavContext.list.findIndex(t => t.title === titleData.title);
    } else {
        currentNavContext.index = -1;
    }

    // Update UI
    const prevBtn = document.getElementById('prevTitleBtn');
    const nextBtn = document.getElementById('nextTitleBtn');

    if (currentNavContext.index !== -1) {
        prevBtn.disabled = currentNavContext.index <= 0;
        nextBtn.disabled = currentNavContext.index >= currentNavContext.list.length - 1;
    } else {
        prevBtn.disabled = true;
        nextBtn.disabled = true;
    }

    resetFooterHideTimer();
}

function navigateModal(direction) {
    if (!currentNavContext.list || currentNavContext.index === -1) return;

    const newIndex = currentNavContext.index + direction;
    if (newIndex >= 0 && newIndex < currentNavContext.list.length) {
        // Need to ensure pathInfo preservation if possible, but showContent takes titleData.
        // The objects in currentGroupedTitles usually have pathInfo if it was set? 
        // In openContentByIndex we injected it. We should inject it here too if missing.
        // But simpler: just pass the object from the list. 
        // Wait, currentGroupedTitles objects don't store the pathInfo permanently unless we modified them in place?
        // openContentByIndex modified the object in the array? Yes: `titleData = ...; titleData.pathInfo = ...`
        // So safe to assume it's good.

        // For search results, we constructed a new object in openSearchResultByIndex?
        // Let's check openSearchResultByIndex. It passed titleWithContext to showContent.
        // It did NOT modify window.currentSearchResults items.
        // So navigating via search results might lose pathInfo unless we reconstruct it.
        // However, if we reuse the logic...

        let nextTitle = currentNavContext.list[newIndex];

        // If coming from search results, nextTitle is just the raw title object from JSON.
        // We need to re-inject path info if it's missing.
        if (!nextTitle.pathInfo && window.currentSearchResults) {
            // Try to find it in search results to get metadata
            const res = window.currentSearchResults.find(r => r.title.title === nextTitle.title);
            if (res) {
                // Reconstruct context
                // Note: we can't easily call openSearchResultByIndex because it takes index in search list.
                // But we have the index in the mapped list, which corresponds to search results index.
                // So we CAN call openSearchResultByIndex if we are in search mode!

                // BUT currentNavContext.list is just a map of titles.
                // If we are in search mode, we should just use openSearchResultByIndex(newIndex).
                if (window.currentSearchResults.length === currentNavContext.list.length) {
                    openSearchResultByIndex(newIndex);
                    return;
                }
            }
        }

        // Check if we are in Theme mode
        if (window.currentGroupedTitles && window.currentGroupedTitles.length === currentNavContext.list.length) {
            openContentByIndex(newIndex);
            return;
        }

        // Fallback
        showContent(nextTitle);
    }
}

function resetFooterHideTimer() {
    const footer = document.getElementById('modalNavFooter');
    if (!footer) return;

    footer.classList.remove('hidden');

    if (footerHideTimeout) clearTimeout(footerHideTimeout);

    footerHideTimeout = setTimeout(() => {
        // Only hide if modal is still open
        if (!document.getElementById('contentModal').classList.contains('hidden')) {
            footer.classList.add('hidden');
        }
    }, 3000);
}

function setupModalFooter() {
    const footer = document.getElementById('modalNavFooter');
    const prevBtn = document.getElementById('prevTitleBtn');
    const nextBtn = document.getElementById('nextTitleBtn');
    const closeBtn = document.getElementById('closeModalFooterBtn');
    const modalBody = document.getElementById('modalBody');

    if (prevBtn) prevBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        navigateModal(-1);
    });

    if (nextBtn) nextBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        navigateModal(1);
    });

    if (closeBtn) closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        closeModal();
    });

    // Auto-hide triggers
    const reset = () => resetFooterHideTimer();

    if (modalBody) {
        modalBody.addEventListener('scroll', reset, { passive: true });
        modalBody.addEventListener('click', reset);
        modalBody.addEventListener('touchstart', reset, { passive: true });
    }
}

// ============================================
// INITIALIZE ON LOAD
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    loadData();
    setupScrollToTop();
    setupModalFooter();
    document.getElementById('closeAllThemesBtn').addEventListener('click', toggleAllThemes);
    renderHistory();
});

// ============================================
// HISTORY NAVIGATION
// ============================================
const HISTORY_KEY = 'shin_college_history';
const MAX_HISTORY = 50;

function saveHistory(titleData) {
    if (!titleData || !titleData.title) return;

    let history = [];
    try {
        history = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
    } catch (e) {
        history = [];
    }

    // Remove if exists to move to top
    history = history.filter(item => item.title !== titleData.title);

    // Store minimal data to save space
    // We only need indices to reconstruct the object later
    const historyItem = {
        title: titleData.title,
        volume: titleData.pathInfo ? titleData.pathInfo.volume : '',
        theme: titleData.pathInfo ? titleData.pathInfo.theme : '',
        // Store indices if available, otherwise we rely on search later
        vIdx: titleData.pathInfo ? titleData.pathInfo.volumeIndex : -1,
        tIdx: titleData.pathInfo ? titleData.pathInfo.themeIndex : -1
    };

    history.unshift(historyItem);

    if (history.length > MAX_HISTORY) history.pop();

    try {
        localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    } catch (e) {
        console.error("Storage quota exceeded", e);
        // Fallback: Clear history and retry with just the current item
        // This handles cases where legacy data is filling the storage
        try {
            // Keep only the current item which is minimal
            const minimalHistory = [historyItem];
            localStorage.setItem(HISTORY_KEY, JSON.stringify(minimalHistory));
            console.log("History reset to minimal due to quota.");
        } catch (e2) {
            console.error("Critical storage failure", e2);
        }
    }
    renderHistory();
}

function openHistoryItem(index) {
    let history = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
    const item = history[index];
    if (item) {
        // Reconstruct data from indices if valid
        if (item.vIdx >= 0 && item.tIdx >= 0 && data[item.vIdx]) {
            const vol = data[item.vIdx];
            const theme = vol.themes[item.tIdx];
            if (theme) {
                // We need to find the specific title object within the theme
                // Since we didn't store title index, we search by title string
                const grouped = groupNumberedTitles(theme.titles);
                const found = grouped.find(g => g.title === item.title);

                if (found) {
                    const titleWithContext = {
                        ...found,
                        pathInfo: {
                            volume: formatVolumeName(vol.volume),
                            theme: theme.theme,
                            volumeIndex: item.vIdx,
                            themeIndex: item.tIdx
                        }
                    };
                    showContent(titleWithContext);
                    return;
                }
            }
        }

        // Fallback: search by title string if indices fail or are missing
        const results = searchContent(item.title);
        // Look for exact match
        const exactMatch = results.find(r => r.title.title === item.title);
        if (exactMatch) {
            openSearchResultByIndex(0); // Not ideal but works for now, or better:
            // We can manually call showContent like we do in openSearchResultByIndex
            const volumeIndex = data.findIndex(v => v.volume === exactMatch.volume);
            const themeIndex = volumeIndex >= 0 ? data[volumeIndex].themes.findIndex(t => t.theme === exactMatch.theme) : -1;

            const titleWithContext = {
                ...exactMatch.title,
                pathInfo: {
                    volume: formatVolumeName(exactMatch.volume),
                    theme: exactMatch.theme,
                    volumeIndex: volumeIndex,
                    themeIndex: themeIndex
                }
            };
            showContent(titleWithContext);
        } else {
            alert("This content could not be found.");
        }
    }
}

function clearHistory() {
    if (confirm('Tem certeza que deseja limpar o histórico?')) {
        localStorage.removeItem(HISTORY_KEY);
        renderHistory();
    }
}

function renderHistory() {
    const list = document.getElementById('historyList');
    const container = document.getElementById('historySection');
    const clearBtn = document.getElementById('clearHistoryBtn');

    if (!list || !container) return;

    let history = [];
    try {
        history = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
    } catch (e) {
        history = [];
    }

    if (history.length === 0) {
        container.classList.add('hidden');
        if (clearBtn) clearBtn.classList.add('hidden');
        return;
    }

    // Show components
    container.classList.remove('hidden');
    if (clearBtn) clearBtn.classList.remove('hidden');

    list.innerHTML = history.map((item, index) => `
        <div class="history-item" onclick="openHistoryItem(${index})">
            <div class="history-item-title">${item.title}</div>
            <div class="history-item-path">${item.volume || ''} → ${item.theme || ''}</div>
        </div>
    `).join('');
}

function openHistoryItem(index) {
    let history = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
    const item = history[index];
    if (item && item.data) {
        showContent(item.data);
    }
}

function toggleHistory() {
    const list = document.getElementById('historyList');
    const icon = document.getElementById('historyArrow');

    if (list.classList.contains('open')) {
        list.classList.remove('open');
        icon.style.transform = 'rotate(0deg)';
    } else {
        list.classList.add('open');
        icon.style.transform = 'rotate(180deg)';
    }
}



function updateModalFooter(titleData) {
    const footer = document.getElementById('modalNavFooter');
    if (!footer) return;

    // Determine context
    currentNavContext.list = null;

    // Check if in current grouped titles (Theme)
    if (window.currentGroupedTitles && window.currentGroupedTitles.some(t => t.title === titleData.title)) {
        currentNavContext.list = window.currentGroupedTitles;
    }
    // Check if in search results
    else if (window.currentSearchResults && window.currentSearchResults.some(r => r.title.title === titleData.title)) {
        currentNavContext.list = window.currentSearchResults.map(r => r.title);
    }
    // Context Recovery: If missing, attempt to reconstruct from pathInfo
    else if (titleData.pathInfo && typeof data !== 'undefined') {
        const vol = data[titleData.pathInfo.volumeIndex];
        if (vol && vol.themes[titleData.pathInfo.themeIndex]) {
            // Reconstruct the title list for this theme
            currentNavContext.list = vol.themes[titleData.pathInfo.themeIndex].titles;
        }
    }

    // Find index
    if (currentNavContext.list) {
        // Use loose comparison for safety or fallback to string match
        currentNavContext.index = currentNavContext.list.findIndex(t => {
            const tTitle = (t.title || t).toString().trim();
            const currentTitle = (titleData.title || titleData).toString().trim();
            // Try strict match first, then loose
            if (tTitle === currentTitle) return true;
            // Handle cases where title might differ slightly in structure but be logically same
            if (t.pathInfo && titleData.pathInfo) {
                return t.pathInfo.volumeIndex === titleData.pathInfo.volumeIndex &&
                    t.pathInfo.themeIndex === titleData.pathInfo.themeIndex &&
                    t.pathInfo.titleIndex === titleData.pathInfo.titleIndex;
            }
            return false;
        });
    } else {
        currentNavContext.index = -1;
    }

    // Update UI
    const prevBtn = document.getElementById('prevTitleBtn');
    const nextBtn = document.getElementById('nextTitleBtn');

    // Check for valid items in each direction
    let hasPrev = false;
    let hasNext = false;

    // Check Previous
    for (let i = currentNavContext.index - 1; i >= 0; i--) {
        if (currentNavContext.list[i].title !== '---') {
            hasPrev = true;
            break;
        }
    }

    // Check Next
    for (let i = currentNavContext.index + 1; i < currentNavContext.list.length; i++) {
        if (currentNavContext.list[i].title !== '---') {
            hasNext = true;
            break;
        }
    }

    if (currentNavContext.index !== -1) {
        prevBtn.disabled = !hasPrev;
        nextBtn.disabled = !hasNext;
    } else {
        prevBtn.disabled = true;
        nextBtn.disabled = true;
    }

    resetFooterHideTimer();
}

function navigateModal(direction) {
    if (!currentNavContext.list || currentNavContext.index === -1) return;

    let newIndex = currentNavContext.index + direction;

    // Loop to skip separators ('---')
    while (newIndex >= 0 && newIndex < currentNavContext.list.length) {
        if (currentNavContext.list[newIndex].title !== '---') {
            break;
        }
        newIndex += direction;
    }

    if (newIndex < 0 || newIndex >= currentNavContext.list.length) return;

    let nextTitle = currentNavContext.list[newIndex];

    // Ensure pathInfo exists by copying from current title if needed
    if (!nextTitle.pathInfo && currentTitleData && currentTitleData.pathInfo) {
        // Calculate the new title index if we know the theme structure
        if (typeof data !== 'undefined') {
            const vol = data[currentTitleData.pathInfo.volumeIndex];
            if (vol && vol.themes[currentTitleData.pathInfo.themeIndex]) {
                const themeList = vol.themes[currentTitleData.pathInfo.themeIndex].titles;
                const actualIndex = themeList.findIndex(t => (t.title || t) === (nextTitle.title || nextTitle));
                if (actualIndex !== -1) {
                    nextTitle = {
                        ...nextTitle,
                        pathInfo: {
                            volume: currentTitleData.pathInfo.volume,
                            theme: currentTitleData.pathInfo.theme,
                            volumeIndex: currentTitleData.pathInfo.volumeIndex,
                            themeIndex: currentTitleData.pathInfo.themeIndex,
                            titleIndex: actualIndex
                        }
                    };
                }
            }
        }
    }

    // Always use showContent - it handles everything correctly
    showContent(nextTitle);
}

function resetFooterHideTimer() {
    const footer = document.getElementById('modalNavFooter');
    if (!footer) return;

    footer.classList.remove('hidden');

    if (footerHideTimeout) clearTimeout(footerHideTimeout);

    footerHideTimeout = setTimeout(() => {
        // Only hide if modal is still open
        if (!document.getElementById('contentModal').classList.contains('hidden')) {
            footer.classList.add('hidden');
        }
    }, 5000);
}

function setupModalFooter() {
    const footer = document.getElementById('modalNavFooter');
    const prevBtn = document.getElementById('prevTitleBtn');
    const nextBtn = document.getElementById('nextTitleBtn');
    const closeBtn = document.getElementById('closeModalFooterBtn');

    if (prevBtn) prevBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        navigateModal(-1);
    });

    if (nextBtn) nextBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        navigateModal(1);
    });

    if (closeBtn) closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        closeModal();
    });

    // Auto-hide triggers - Listen globally for better reliability
    const reset = () => resetFooterHideTimer();

    window.addEventListener('scroll', reset, { passive: true });
    document.addEventListener('click', reset);
    document.addEventListener('touchstart', reset, { passive: true });
    document.addEventListener('mousemove', reset, { passive: true });
}
