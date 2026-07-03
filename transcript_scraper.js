(function() {
    // 100 Official Company Names mapped exactly to run_extraction.py
    const OFFICIAL_COMPANIES = [
        "John Deere", "Nike", "Banco Bradesco", "Deutsche Post", "Cr\xE9dit Mutuel",
        "Bayer", "Saint-Gobain", "Volvo Group", "Iberdrola", "Veolia Environnement",
        "Bristol Myers Squibb", "Landesbank Baden-W\xFCrttemberg", "General Dynamics", "L'Or\xE9al", "Travelers",
        "Swiss Re", "Eli Lilly", "Orange", "Telef\xF3nica", "Woolworths",
        "Vodafone", "DZ Bank", "Dow", "ANZ Group", "Commonwealth Bank",
        "Thermo Fisher Scientific", "Novo Nordisk", "Abbott Laboratories", "Standard Chartered", "Inditex",
        "Best Buy", "Schneider Electric", "KB Financial Group", "Northrop Grumman", "National Australia Bank",
        "LyondellBasell", "GSK", "Cenovus Energy", "Warner Bros", "Netflix",
        "Qualcomm", "Honeywell", "Vale", "Salesforce", "Philip Morris",
        "Westpac Banking", "AIA Group", "SAP", "Mondelez", "Starbucks",
        "Visa", "CBRE Group", "ICICI Bank", "International Airlines Group", "PNC Financial",
        "Emirates", "Cummins", "Air France", "Paccar", "Metro Group",
        "BAE Systems", "Amgen", "Linde", "ABB", "Ecopetrol",
        "Medtronic", "Heineken", "JBS", "Uniper", "Korea Electric Power",
        "Itau Unibanco", "Raizen", "Energie Baden-W\xFCrttemberg", "CFE", "Standard Bank",
        "Nedbank", "Absa Group", "Atlassian", "ENBW", "MTN Group",
        "RWE", "KEPCO", "Duke Energy", "Air New Zealand", "MercadoLibre",
        "Embraer", "Wesfarmers", "Sappi", "Fortis", "James Hardie",
        "Metalurgica Gerdau", "Anywhere Real Estate", "Sasol", "Colliers International", "Suncorp",
        "Grupo Argos", "Adcorp", "Warehouse Group", "Nubank", "Natura & Co"
    ];

    // Document type name mappings to follow the user's strict naming structure
    const DOC_TYPE_FORMATS = {
        "Code of Conduct": "Code of Conduct",
        "Ethics & Compliance Policy": "Ethics & Compliance Policy",
        "Responsible AI & AI Ethics Guidelines": "Responsible AI _ AI Ethics Guidelines",
        "SDG ESG Report": "ESG _ SDG Sustainability Report",
        "Annual Report": "Annual Report",
        "Earnings Call Transcript": "Earnings Call Transcript (Q4_FY only)",
        "Proxy Statement / Corp Gov Report": "Proxy Statement _ Corporate Governance Report",
        "Supplier Code of Conduct": "Supplier Code of Conduct"
    };

    // Specific Company name overrides to match exact data collection standards
    const COMPANY_NAME_OVERRIDES = {
        "Westpac Banking": "Westpac Banking Group",
        "Philip Morris": "Philip Morris International",
        "Honeywell": "Honeywell International",
        "AIA Group": "AIA Group"
    };

    // Get current text and URL to auto-detect metadata
    const pageText = document.body.innerText;
    const pageTitle = document.title;
    const pageUrl = window.location.href;

    // 1. Auto-detect Company Name
    let detectedCompany = "";
    let bestMatchLength = 0;

    for (const company of OFFICIAL_COMPANIES) {
        const escaped = company.replace(/[^a-zA-Z0-9]/g, '\\s*');
        const regex = new RegExp(escaped, 'i');
        
        if (regex.test(pageTitle) || regex.test(pageUrl)) {
            if (company.length > bestMatchLength) {
                detectedCompany = company;
                bestMatchLength = company.length;
            }
        }
    }

    if (!detectedCompany) {
        for (const company of OFFICIAL_COMPANIES) {
            const escaped = company.replace(/[^a-zA-Z0-9]/g, '\\s*');
            const regex = new RegExp('\\b' + escaped + '\\b', 'i');
            if (regex.test(pageText)) {
                if (company.length > bestMatchLength) {
                    detectedCompany = company;
                    bestMatchLength = company.length;
                }
            }
        }
    }

    // 2. Auto-detect Year
    let detectedYear = "";
    const yearMatches = (pageTitle + " " + pageUrl).match(/\b(20\d{2})\b/g);
    if (yearMatches && yearMatches.length > 0) {
        detectedYear = yearMatches[0];
    } else {
        detectedYear = new Date().getFullYear().toString();
    }

    // 3. User Prompt Loop for Company Verification
    let finalCompany = detectedCompany || "John Deere";
    let isCompanyValid = false;

    while (!isCompanyValid) {
        const userInput = prompt(
            `Verify the COMPANY NAME:\n\n` +
            `• Must match the official name exactly.\n` +
            `• Enter 'list' to see all 100 official names.\n\n` +
            `Current name:`, 
            finalCompany
        );

        if (userInput === null) return; // User cancelled

        const cleanInput = userInput.trim();
        if (cleanInput.toLowerCase() === 'list') {
            alert("Official Companies:\n\n" + OFFICIAL_COMPANIES.join("\n"));
            continue;
        }

        const matchedOfficial = OFFICIAL_COMPANIES.find(c => c.toLowerCase() === cleanInput.toLowerCase());

        if (matchedOfficial) {
            finalCompany = matchedOfficial;
            isCompanyValid = true;
        } else {
            const proceed = confirm(
                `WARNING: "${cleanInput}" is NOT in the official 100 companies list!\n\n` +
                `This will cause extraction issues unless it's a new company.\n` +
                `Do you want to use this name anyway?`
            );
            if (proceed) {
                finalCompany = cleanInput;
                isCompanyValid = true;
            }
        }
    }

    // Apply company overrides (like "Westpac Banking" -> "Westpac Banking Group")
    if (COMPANY_NAME_OVERRIDES[finalCompany]) {
        finalCompany = COMPANY_NAME_OVERRIDES[finalCompany];
    }

    // Format company name with underscores instead of spaces
    const companyFormatted = finalCompany.trim().replace(/\s+/g, '_');

    // 4. Prompt for Year
    const finalYear = prompt("Enter the year (YYYY):", detectedYear);
    if (finalYear === null) return;

    // 5. Prompt for Document Type
    // Show user a list of formatted types to choose from
    const formattedTypesList = Object.keys(DOC_TYPE_FORMATS).map(k => `• ${k} -> ${DOC_TYPE_FORMATS[k]}`).join("\n");
    let chosenDocType = "Earnings Call Transcript";
    let isDocTypeValid = false;

    while (!isDocTypeValid) {
        const docInput = prompt(
            `Enter or verify the Document Type:\n\n` +
            `Standard Mappings:\n${formattedTypesList}\n\n` +
            `Current choice:`,
            chosenDocType
        );

        if (docInput === null) return;

        const cleanDocInput = docInput.trim();
        // Check if user input matches a key in our map
        const matchedKey = Object.keys(DOC_TYPE_FORMATS).find(k => k.toLowerCase() === cleanDocInput.toLowerCase());
        
        if (matchedKey) {
            chosenDocType = DOC_TYPE_FORMATS[matchedKey];
            isDocTypeValid = true;
        } else {
            // Check if it already matches one of the values
            const matchedValue = Object.values(DOC_TYPE_FORMATS).find(v => v.toLowerCase() === cleanDocInput.toLowerCase());
            if (matchedValue) {
                chosenDocType = matchedValue;
                isDocTypeValid = true;
            } else {
                const proceed = confirm(`WARNING: "${cleanDocInput}" is not in the standard mappings.\n\nUse this custom document type name anyway?`);
                if (proceed) {
                    chosenDocType = cleanDocInput;
                    isDocTypeValid = true;
                }
            }
        }
    }

    // Generate strict filename: YYYY - Formatted Doc Type - Company_Name.txt
    const filename = `${finalYear.trim()} - ${chosenDocType} - ${companyFormatted}.txt`;

    // 6. Text Extraction
    const textContainer = document.querySelector('.item-page') || document.querySelector('main') || document.body;
    const titleElement = document.querySelector('h2') || document.querySelector('h1');
    const paragraphs = textContainer.querySelectorAll('h1, h2, h3, h4, p, li');
    
    let transcriptText = `Source URL: ${pageUrl}\n\n`;
    if (titleElement) {
        transcriptText += `=== ${titleElement.innerText.trim()} ===\n\n`;
    }

    const seenParagraphs = new Set();

    paragraphs.forEach(p => {
        const text = p.innerText.trim();
        
        if (text && 
            text.length > 2 && 
            !seenParagraphs.has(text) && 
            !text.startsWith("Stock Analysis App") && 
            !text.includes("Play Audio") &&
            !text.includes("Download Transcript") &&
            !text.includes("Get it on Google Play") &&
            !text.includes("Daily market news in bullet point")) {
            
            seenParagraphs.add(text);

            if (p.tagName.startsWith('H')) {
                y = `\n[${text}]\n`;
                transcriptText += y;
            } else if (p.tagName === 'LI') {
                transcriptText += `\u2022 ${text}\n`;
            } else if (text.match(/^[A-Z][a-zA-Z\s\.\-]+:/) || text.startsWith("Great.") || text.startsWith("All right.")) {
                transcriptText += `\n${text}\n`;
            } else {
                transcriptText += `${text}\n`;
            }
        }
    });

    if (transcriptText.split('\n').length < 10) {
        transcriptText = `Source URL: ${pageUrl}\n\n` + textContainer.innerText;
    }

    // 7. Download
    const blob = new Blob([transcriptText], { type: 'text/plain;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
    
    console.log(`Success! Clean transcript file downloaded: ${filename}`);
})();
