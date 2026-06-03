document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const fileDropArea = document.getElementById('file-drop-area');
    const fileMsg = document.querySelector('.file-msg');
    const uploadSection = document.getElementById('upload-section');
    const dashboardSection = document.getElementById('dashboard-section');
    const loadingOverlay = document.getElementById('loading-overlay');
    const errorMessage = document.getElementById('error-message');
    const resetBtn = document.getElementById('reset-btn');
    const downloadBtn = document.getElementById('download-btn');

    let scoreChartInstance = null;
    let currentAnalysisData = null;

    // ─── Drag & Drop ─────────────────────────────────────────
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(ev =>
        fileDropArea.addEventListener(ev, e => { e.preventDefault(); e.stopPropagation(); }, false)
    );
    ['dragenter', 'dragover'].forEach(ev =>
        fileDropArea.addEventListener(ev, () => fileDropArea.classList.add('is-active'), false)
    );
    ['dragleave', 'drop'].forEach(ev =>
        fileDropArea.addEventListener(ev, () => fileDropArea.classList.remove('is-active'), false)
    );
    fileDropArea.addEventListener('drop', e => {
        fileInput.files = e.dataTransfer.files;
        updateFileMsg();
    });
    fileInput.addEventListener('change', updateFileMsg);

    function updateFileMsg() {
        fileMsg.textContent = fileInput.files.length > 0
            ? `✅ Selected: ${fileInput.files[0].name}`
            : 'Drag and drop your resume here, or click to browse';
    }

    // ─── Form Submit ─────────────────────────────────────────
    uploadForm.addEventListener('submit', async e => {
        e.preventDefault();
        if (!fileInput.files.length) { showError('Please select a file.'); return; }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        errorMessage.classList.add('hidden');
        loadingOverlay.classList.remove('hidden');

        try {
            const response = await fetch('/api/analyze', { method: 'POST', body: formData });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Analysis failed.');
            currentAnalysisData = data;
            renderDashboard(data);
            uploadSection.classList.add('hidden');
            dashboardSection.classList.remove('hidden');
            window.scrollTo({ top: 0, behavior: 'smooth' });
        } catch (err) {
            showError(err.message);
        } finally {
            loadingOverlay.classList.add('hidden');
        }
    });

    // ─── Download PDF ─────────────────────────────────────────
    downloadBtn.addEventListener('click', async () => {
        if (!currentAnalysisData) return;
        const orig = downloadBtn.textContent;
        downloadBtn.textContent = 'Generating…';
        downloadBtn.disabled = true;
        try {
            const res = await fetch('/api/download-report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(currentAnalysisData)
            });
            if (!res.ok) throw new Error('Failed to generate report');
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url; a.download = 'Resume_Analysis_Report.pdf';
            document.body.appendChild(a); a.click();
            URL.revokeObjectURL(url); a.remove();
        } catch (err) { alert(err.message); }
        finally { downloadBtn.textContent = orig; downloadBtn.disabled = false; }
    });

    // ─── Reset ───────────────────────────────────────────────
    resetBtn.addEventListener('click', () => {
        dashboardSection.classList.add('hidden');
        uploadSection.classList.remove('hidden');
        uploadForm.reset();
        updateFileMsg();
        currentAnalysisData = null;
    });

    function showError(msg) {
        errorMessage.textContent = msg;
        errorMessage.classList.remove('hidden');
    }

    // ─── Render Dashboard ────────────────────────────────────
    function renderDashboard(data) {
        renderProfessionBanner(data);
        renderATSChart(data.ats_score || 0);
        renderCategoryBars(data.category_scores);
        renderTags('tech-skills-list', data.technical_skills);
        renderTags('soft-skills-list', data.soft_skills);
        renderExplainedList('missing-keywords-list', data.missing_keywords, 'keyword', 'explanation');
        renderExplainedList('missing-skills-list', data.missing_skills, 'skill', 'explanation');
        renderExplainedList('weak-sections-list', data.weak_sections, 'section', 'explanation');
        renderExplainedList('content-improvements-list', data.content_improvements, 'suggestion', 'explanation');
        renderExplainedList('ats-optimization-list', data.ats_optimization, 'suggestion', 'explanation');
        renderCareerGrowth(data.career_growth_suggestions);
        renderAISolutions(data.ai_solutions);
    }

    function renderProfessionBanner(data) {
        document.getElementById('prof-profession').textContent = data.detected_profession || 'Unknown';
        document.getElementById('prof-industry').textContent = data.industry || 'Unknown';
        const levelEl = document.getElementById('prof-level');
        levelEl.textContent = data.experience_level || 'Unknown';
        // Color badge by level
        const level = (data.experience_level || '').toLowerCase();
        levelEl.className = 'profession-value exp-badge';
        if (level.includes('fresher') || level.includes('student')) levelEl.classList.add('badge-fresher');
        else if (level.includes('senior') || level.includes('executive')) levelEl.classList.add('badge-senior');
        else levelEl.classList.add('badge-mid');
    }

    function renderATSChart(score) {
        const ctx = document.getElementById('scoreChart').getContext('2d');
        let color = '#dc2626';
        let feedback = 'Needs significant improvement';
        if (score >= 60) { color = '#d97706'; feedback = 'Average – has room to grow'; }
        if (score >= 75) { color = '#2563eb'; feedback = 'Good – a few tweaks needed'; }
        if (score >= 88) { color = '#059669'; feedback = 'Excellent resume!'; }

        if (scoreChartInstance) scoreChartInstance.destroy();

        scoreChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [score, 100 - score],
                    backgroundColor: [color, 'rgba(0,0,0,0.07)'],
                    borderWidth: 0
                }]
            },
            options: {
                cutout: '82%',
                responsive: true,
                maintainAspectRatio: false,
                plugins: { tooltip: { enabled: false } }
            },
            plugins: [{
                id: 'centerText',
                beforeDraw(chart) {
                    const { width, height, ctx } = chart;
                    ctx.restore();
                    ctx.font = `bold ${(height / 100).toFixed(2)}em Outfit`;
                    ctx.textBaseline = 'middle';
                    ctx.fillStyle = '#1e293b';
                    const text = `${score}%`;
                    ctx.fillText(text, Math.round((width - ctx.measureText(text).width) / 2), height / 2);
                    ctx.save();
                }
            }]
        });

        const el = document.getElementById('score-text');
        el.textContent = feedback;
        el.style.color = color;
    }

    function renderCategoryBars(scores) {
        const container = document.getElementById('category-bars');
        container.innerHTML = '';
        if (!scores) return;
        for (const [key, val] of Object.entries(scores)) {
            let barColor = '#dc2626';
            if (val >= 60) barColor = '#d97706';
            if (val >= 80) barColor = '#059669';
            const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            container.innerHTML += `
                <div class="progress-item">
                    <div class="progress-label"><span>${label}</span><span>${val}/100</span></div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width:0%;background:${barColor};" data-w="${val}%"></div>
                    </div>
                </div>`;
        }
        setTimeout(() => {
            container.querySelectorAll('.progress-bar-fill').forEach(el => {
                el.style.width = el.dataset.w;
            });
        }, 120);
    }

    // ─── Render Helpers ──────────────────────────────────────

    /** Renders items that are EITHER simple strings OR objects with {key, explain} */
    function renderExplainedList(containerId, items, keyField, explainField) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';
        if (!items || !items.length) {
            container.innerHTML = '<p class="none-text">None identified.</p>';
            return;
        }
        items.forEach(item => {
            const div = document.createElement('div');
            div.className = 'explained-item';
            if (typeof item === 'string') {
                div.innerHTML = `<span class="explained-title">${item}</span>`;
            } else {
                const title = item[keyField] || '';
                const explain = item[explainField] || '';
                div.innerHTML = `
                    <span class="explained-title">${title}</span>
                    ${explain ? `<p class="explained-reason">${explain}</p>` : ''}`;
            }
            container.appendChild(div);
        });
    }

    function renderCareerGrowth(items) {
        const container = document.getElementById('career-growth-list');
        container.innerHTML = '';
        if (!items || !items.length) {
            container.innerHTML = '<p class="none-text">No suggestions available.</p>';
            return;
        }
        items.forEach((item, i) => {
            const card = document.createElement('div');
            card.className = 'growth-card';
            const suggestion = typeof item === 'string' ? item : item.suggestion || '';
            const explanation = typeof item === 'object' ? (item.explanation || '') : '';
            card.innerHTML = `
                <div class="growth-icon">${i + 1}</div>
                <div>
                    <p class="growth-title">${suggestion}</p>
                    ${explanation ? `<p class="growth-reason">${explanation}</p>` : ''}
                </div>`;
            container.appendChild(card);
        });
    }

    function renderAISolutions(ai) {
        if (!ai) return;
        document.getElementById('ai-summary').textContent = ai.improved_summary || 'No suggestions.';
        document.getElementById('ai-skills-advice').textContent = ai.skills_presentation_advice || 'No suggestions.';
        const achList = document.getElementById('ai-achievements');
        achList.innerHTML = '';
        (ai.improved_achievements || []).forEach(a => {
            const li = document.createElement('li'); li.textContent = a;
            achList.appendChild(li);
        });
    }

    function renderTags(containerId, items) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';
        if (!items || !items.length) {
            container.innerHTML = '<span class="none-text">None found.</span>';
            return;
        }
        items.forEach(item => {
            const span = document.createElement('span');
            span.className = 'tag';
            span.textContent = item;
            container.appendChild(span);
        });
    }
});
