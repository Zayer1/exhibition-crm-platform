const resultsPanel = document.getElementById('resultsPanel');
const detailsPanel = document.getElementById('detailsPanel');
let currentCompany = null;
let currentOpportunity = null;

async function searchExhibitors() {
    const query = document.getElementById('searchInput').value;
    if (!query) return;

    resultsPanel.innerHTML = '<p>Searching...</p>';
    detailsPanel.classList.add('hidden');

    try {
        const response = await fetch(`/search?query=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        resultsPanel.innerHTML = '';
        if (data.length === 0) {
            resultsPanel.innerHTML = '<p>No results found.</p>';
            return;
        }

        data.forEach(company => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <h3>${company.company_name}</h3>
                <p>Code: ${company.company_code}</p>
                <p>${company.opportunities.length} Opportunities</p>
            `;
            card.onclick = () => showCompanyDetails(company);
            resultsPanel.appendChild(card);
        });
    } catch (err) {
        resultsPanel.innerHTML = '<p style="color: #f87171;">Failed to fetch results.</p>';
    }
}

function showCompanyDetails(company) {
    currentCompany = company;
    detailsPanel.classList.remove('hidden');
    
    let html = `
        <div class="details-header">
            <h2>${company.company_name}</h2>
            <p>Region: ${company.region || 'N/A'} | Rep: ${company.sales_rep || 'N/A'}</p>
        </div>
        <h3>Opportunities</h3>
        <div style="margin-top: 1rem;">
    `;

    if (company.opportunities.length === 0) {
        html += `<p>No active opportunities.</p>`;
    } else {
        company.opportunities.forEach(opp => {
            html += `
                <div class="card" onclick="showOpportunity('${opp.opportunity_code}')">
                    <h3>Fair: ${opp.fair_edition_code}</h3>
                    <p>Status: ${opp.status || 'New'}</p>
                    <p>Amount: €${opp.amount_eur || 0}</p>
                </div>
            `;
        });
    }
    
    html += `</div>`;
    detailsPanel.innerHTML = html;
}

async function showOpportunity(code) {
    const res = await fetch(`/opportunities/${code}`);
    const opp = await res.json();
    currentOpportunity = opp;

    const handoffsRes = await fetch(`/opportunities/${code}/handoffs`);
    const handoffs = await handoffsRes.json();

    const activitiesRes = await fetch(`/opportunities/${code}/activities`);
    const activities = await activitiesRes.json();

    let html = `
        <button onclick="showCompanyDetails(currentCompany)" style="margin-bottom: 1rem; background: rgba(255,255,255,0.1);">Back</button>
        <div class="details-header">
            <h2>Opportunity: ${opp.fair_edition_code}</h2>
            <p>Status: <span class="badge" style="background: rgba(255,255,255,0.2);">${opp.status || 'Open'}</span></p>
        </div>

        <div class="opp-grid">
            <div class="metric-box">
                <label>Status</label>
                <input type="text" id="editStatus" value="${opp.status || ''}" style="width: 100%;">
            </div>
            <div class="metric-box">
                <label>Budget (€)</label>
                <input type="number" id="editBudget" value="${opp.client_budget_eur || 0}" style="width: 100%;">
            </div>
            <div class="metric-box">
                <label>Stand Area (sqm)</label>
                <input type="number" id="editArea" value="${opp.stand_area_sqm || 0}" style="width: 100%;">
            </div>
            <div class="metric-box">
                <label>Req. Height (m)</label>
                <input type="number" id="editHeight" value="${opp.requested_height_m || 0}" style="width: 100%;">
            </div>
        </div>
        <button onclick="updateOpportunity('${code}')" style="margin-bottom: 2rem;">Save Changes</button>

        <div style="margin-bottom: 2rem; background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 8px;">
            <h3>Record Activity & Follow-up</h3>
            <div style="display: flex; gap: 1rem; margin-top: 1rem;">
                <input type="text" id="actType" placeholder="Type (e.g. Call, Email)" style="width: 150px;">
                <input type="text" id="actDetails" placeholder="Conversation details..." style="flex: 1;">
            </div>
            <div style="display: flex; gap: 1rem; margin-top: 1rem; align-items: center;">
                <label>Follow-up Date:</label>
                <input type="date" id="actDate" style="width: 150px;">
                <button onclick="addActivity('${code}')">Save Activity</button>
            </div>
            
            <h4 style="margin-top: 1rem;">Past Activities</h4>
            <ul style="margin-top: 0.5rem; padding-left: 1.5rem; color: #cbd5e1; font-size: 0.9rem;">
                ${activities.map(a => `<li><b>${a.occurred_at.split('T')[0]} - ${a.activity_type}</b>: ${a.details} ${a.follow_up_on ? `(Follow-up: ${a.follow_up_on})` : ''}</li>`).join('')}
            </ul>
        </div>

        <div class="handoff-panel" id="handoffPanel">
            <h3>Handoff Assistant</h3>
            <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 1rem;">Generate a technical brief and verify constraints automatically.</p>
            <button onclick="runHandoff('${opp.opportunity_code}')">Run Assistant</button>
            <div id="handoffResult" style="margin-top: 1rem;"></div>
            
            <h4 style="margin-top: 2rem;">Past Runs</h4>
            <div style="max-height: 200px; overflow-y: auto; margin-top: 0.5rem; font-size: 0.85rem;">
                ${handoffs.reverse().map(r => `
                    <div style="background: rgba(0,0,0,0.3); padding: 0.5rem; margin-bottom: 0.5rem; border-radius: 4px;">
                        <b>Decision:</b> ${r.coordinator_decision} <br>
                        <b>Issues:</b> ${r.checker_output.issues.join(', ') || 'None'}
                    </div>
                `).join('')}
            </div>
        </div>
    `;

    detailsPanel.innerHTML = html;
}

async function updateOpportunity(code) {
    const budgetVal = document.getElementById('editBudget').value;
    const areaVal = document.getElementById('editArea').value;
    const heightVal = document.getElementById('editHeight').value;

    const data = {
        status: document.getElementById('editStatus').value || undefined,
        client_budget_eur: budgetVal === "" ? null : parseFloat(budgetVal),
        stand_area_sqm: areaVal === "" ? null : parseFloat(areaVal),
        requested_height_m: heightVal === "" ? null : parseFloat(heightVal)
    };
    await fetch(`/opportunities/${code}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    showOpportunity(code);
}

async function addActivity(code) {
    const actType = document.getElementById('actType').value;
    const details = document.getElementById('actDetails').value;
    const date = document.getElementById('actDate').value;
    
    if(!actType || !details) {
        alert("Type and Details are required");
        return;
    }

    const data = {
        activity_type: actType,
        details: details,
        author: "Sales Rep",
        follow_up_on: date ? date : null
    };

    await fetch(`/opportunities/${code}/activities`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    showOpportunity(code);
}

async function runHandoff(code) {
    const resDiv = document.getElementById('handoffResult');
    resDiv.innerHTML = '<p>Running agent...</p>';
    
    try {
        const res = await fetch(`/opportunities/${code}/handoff`, { method: 'POST' });
        const data = await res.json();
        
        const isPass = data.checker_output.status === 'PASS';
        const badgeClass = isPass ? 'pass' : 'fail';

        let issuesHtml = '';
        if (!isPass) {
            issuesHtml = `<ul style="margin-top: 0.5rem; color: #f87171; padding-left: 1rem;">`;
            data.checker_output.issues.forEach(i => issuesHtml += `<li>${i}</li>`);
            issuesHtml += `</ul>`;
        }

        resDiv.innerHTML = `
            <div style="background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                <h4 style="margin-bottom: 0.5rem;">Coordinator Decision: <span class="badge ${badgeClass}">${data.coordinator_decision}</span></h4>
                <p style="font-size: 0.9rem; color: #cbd5e1;">${data.inputs.generated_summary}</p>
                ${issuesHtml}
            </div>
        `;
        
        // Refresh opportunity to update past runs
        setTimeout(() => showOpportunity(code), 2000);
    } catch (e) {
        resDiv.innerHTML = '<p style="color: #f87171;">Error running handoff.</p>';
    }
}

async function showFollowups() {
    resultsPanel.innerHTML = '<p>Loading follow-ups...</p>';
    detailsPanel.classList.add('hidden');

    try {
        const response = await fetch(`/activities/followups`);
        const data = await response.json();
        
        resultsPanel.innerHTML = '<h2>Upcoming Follow-ups</h2><br>';
        if (data.length === 0) {
            resultsPanel.innerHTML += '<p>No follow-ups scheduled.</p>';
            return;
        }

        data.forEach(act => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <h3>${act.activity_type} - ${act.follow_up_on}</h3>
                <p><b>Company:</b> ${act.company_code}</p>
                <p><b>Opp:</b> ${act.opportunity_code || 'N/A'}</p>
                <p>${act.details}</p>
            `;
            // If it's linked to an opportunity, let them click it
            if(act.opportunity_code) {
                card.onclick = async () => {
                    // We need the company context. We can fetch the opp to get the company.
                    const res = await fetch(`/opportunities/${act.opportunity_code}`);
                    const opp = await res.json();
                    
                    const compRes = await fetch(`/search?query=${opp.company_code}`);
                    const comps = await compRes.json();
                    if(comps.length > 0) {
                        currentCompany = comps[0];
                    }
                    showOpportunity(act.opportunity_code);
                };
            }
            resultsPanel.appendChild(card);
        });
    } catch (err) {
        resultsPanel.innerHTML = '<p style="color: #f87171;">Failed to fetch follow-ups.</p>';
    }
}

