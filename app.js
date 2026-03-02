// 加载数据
async function loadData() {
    try {
        const response = await fetch('data.json');
        const data = await response.json();
        renderCompanies(data);
        renderComparisonTable(data);
        document.getElementById('updateTime').textContent = data.updateTime;
    } catch (error) {
        console.error('加载数据失败:', error);
    }
}

// 渲染公司卡片
function renderCompanies(data) {
    // 一线
    const tier1Container = document.getElementById('tier1Companies');
    tier1Container.innerHTML = data.companies.tier1.map(company => createCompanyCard(company)).join('');
    
    // 二线
    const tier2Container = document.getElementById('tier2Companies');
    tier2Container.innerHTML = data.companies.tier2.map(company => createCompanyCard(company)).join('');
    
    // 三线
    const tier3Container = document.getElementById('tier3Companies');
    tier3Container.innerHTML = data.companies.tier3.map(company => createCompanyCard(company)).join('');
}

// 创建公司卡片
function createCompanyCard(company) {
    const changeClass = company.change >= 0 ? 'up' : 'down';
    const changeSign = company.change >= 0 ? '+' : '';
    
    return `
        <a href="${company.link}" class="company-card">
            <div class="company-name">${company.name}</div>
            <div class="company-code">${company.code}</div>
            <div class="company-price">¥${company.price.toFixed(2)}</div>
            <div class="company-change ${changeClass}">${changeSign}${company.change.toFixed(2)}%</div>
        </a>
    `;
}

// 渲染对比表格
function renderComparisonTable(data) {
    const tbody = document.getElementById('comparisonBody');
    const allCompanies = [
        ...data.companies.tier1,
        ...data.companies.tier2,
        ...data.companies.tier3
    ];
    
    tbody.innerHTML = allCompanies.map(company => {
        const growthClass = parseFloat(company.revenueGrowth) >= 15 ? 'positive' : 
                           parseFloat(company.revenueGrowth) >= 10 ? '' : 'negative';
        
        return `
            <tr>
                <td><strong>${company.name}</strong></td>
                <td>${company.marketCap}</td>
                <td>${company.pe}</td>
                <td>${company.grossMargin}</td>
                <td>${company.roe}</td>
                <td class="${growthClass}">${company.revenueGrowth}</td>
            </tr>
        `;
    }).join('');
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', loadData);
