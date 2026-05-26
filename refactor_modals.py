import re

def main():
    file_path = 'AI_Research_Hub.html'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add dialog state and component to App
    dialog_state_code = """
  // GLOBAL DIALOG STATE
  const [dialogConfig, setDialogConfig] = useState(null);
  const [dialogInput, setDialogInput] = useState('');
  const [dialogError, setDialogError] = useState('');

  useEffect(() => {
    window.showGlobalDialog = (config) => {
      setDialogInput('');
      setDialogError('');
      setDialogConfig(config);
    };
  }, []);

  function handleDialogSubmit(e) {
    e.preventDefault();
    if (dialogConfig?.onConfirm) {
       // If it's a prompt, pass the input
       if (dialogConfig.type === 'prompt') {
          dialogConfig.onConfirm(dialogInput);
       } else {
          dialogConfig.onConfirm();
       }
    }
    // We don't automatically close on prompt if the callback handles validation (e.g. error setting)
    // Actually, let's close it by default unless they return a specific symbol?
    // Let's just close it, and if they need to show an error, they can call showGlobalDialog again!
    setDialogConfig(null);
  }
"""

    dialog_ui_code = """
    ),
    dialogConfig && h('div', { className: 'modal-overlay', style: { zIndex: 10000 } },
      h('form', { className: 'modal-content', onSubmit: handleDialogSubmit }, [
        h('div', { className: 'modal-header' }, [
          h('div', { className: 'modal-title' }, dialogConfig.title || 'Notification'),
          h('button', { type: 'button', className: 'modal-close-btn', onClick: () => { if(dialogConfig.onCancel) dialogConfig.onCancel(); setDialogConfig(null); } }, '✕')
        ]),
        h('div', { className: 'modal-body' }, [
          h('div', { className: 'modal-desc', style: { whiteSpace: 'pre-wrap' } }, dialogConfig.message),
          dialogConfig.type === 'prompt' && h('input', {
            className: 'modal-input',
            type: 'password',
            required: true,
            autoFocus: true,
            placeholder: dialogConfig.placeholder || 'Enter value...',
            value: dialogInput,
            style: { marginTop: '16px' },
            onChange: e => { setDialogInput(e.target.value); setDialogError(''); }
          })
        ]),
        h('div', { className: 'modal-actions' }, [
          (dialogConfig.type === 'confirm' || dialogConfig.type === 'prompt') && h('button', { type: 'button', className: 'btn-secondary', style: { padding: '8px 16px', fontSize: '13px' }, onClick: () => { if(dialogConfig.onCancel) dialogConfig.onCancel(); setDialogConfig(null); } }, dialogConfig.cancelText || 'Cancel'),
          h('button', { type: 'submit', className: dialogConfig.danger ? 'btn-primary danger-btn' : 'btn-primary', style: { padding: '8px 16px', fontSize: '13px', ...(dialogConfig.danger ? {backgroundColor: 'var(--red)', borderColor: 'var(--red)'} : {}) } }, dialogConfig.confirmText || 'OK')
        ])
      ])
    ),
    showPasscodeModal && h('div', { className: 'modal-overlay' },
"""

    content = content.replace("  // ADMIN LOCK", dialog_state_code + "\n  // ADMIN LOCK")
    content = content.replace("    showPasscodeModal && h('div', { className: 'modal-overlay' },", dialog_ui_code)

    # 2. Refactor handleLockToggle
    content = content.replace("""  function handleLockToggle() {
    if (isEditMode) { 
      setIsEditMode(false); 
      localStorage.removeItem('fellowship_admin_lock');
      return; 
    }
    setPasscodeInput('');
    setPasscodeError('');
    setShowPasscodeModal(true);
  }""", """  function handleLockToggle() {
    if (isEditMode) { 
      setIsEditMode(false); 
      localStorage.removeItem('fellowship_admin_lock');
      return; 
    }
    window.showGlobalDialog({
      type: 'prompt',
      title: 'Admin Lock',
      message: 'Enter administrator passcode to enable editing of company data and document URLs.',
      confirmText: 'Unlock',
      onConfirm: (val) => {
        if (val === ADMIN_PASSCODE) {
          setIsEditMode(true);
          localStorage.setItem('fellowship_admin_lock', 'unlocked');
        } else {
          window.showGlobalDialog({ type: 'alert', title: 'Error', message: 'Incorrect passcode. Please try again.', danger: true });
        }
      }
    });
  }""")

    # Let's remove the old showPasscodeModal stuff from App return since we use GlobalDialog now
    # Wait, it's safer to keep it for now and manually remove the old render block.
    # I'll just use regex to remove the old showPasscodeModal UI block.
    content = re.sub(r"    showPasscodeModal && h\('div', \{ className: 'modal-overlay'.*?\n    \)\n", "", content, flags=re.DOTALL)
    # Remove the state vars
    content = content.replace("  const [showPasscodeModal, setShowPasscodeModal] = useState(false);\n", "")
    content = content.replace("  const [passcodeInput, setPasscodeInput] = useState('');\n", "")
    content = content.replace("  const [passcodeError, setPasscodeError] = useState('');\n", "")
    content = re.sub(r"  function handlePasscodeSubmit.*?\}\n", "", content, flags=re.DOTALL)


    # 3. Refactor ManageCompaniesView functions
    # addCompany / handleSubmit
    old_add = """    if (!isEditMode) {
      alert("Please unlock Edit Mode to add companies.");
      return;
    }
    if (prompt("Enter master passcode to confirm adding this company:") !== "admin123") {
      alert("Incorrect passcode.");
      return;
    }
    if (!name.trim() || !country.trim()) return;

    const finalSector = isCustomSector ? customSector.trim() : sector;
    if (!finalSector) return;"""
    new_add = """    if (!isEditMode) {
      window.showGlobalDialog({ type: 'alert', title: 'Edit Mode Locked', message: 'Please unlock Edit Mode to add companies.' });
      return;
    }
    window.showGlobalDialog({
      type: 'prompt',
      title: 'Master Passcode',
      message: 'Enter master passcode to confirm adding this company:',
      confirmText: 'Verify & Add',
      onConfirm: (val) => {
        if (val !== "admin123") {
          window.showGlobalDialog({ type: 'alert', title: 'Error', message: 'Incorrect passcode.', danger: true });
          return;
        }
        if (!name.trim() || !country.trim()) return;
        const finalSector = isCustomSector ? customSector.trim() : sector;
        if (!finalSector) return;
        
        const newId = companies.length > 0 ? Math.max(...companies.map(c => c.id)) + 1 : 1;
        const newCompany = { id: newId, name: name.trim(), sector: finalSector, industry: industry.trim() || 'General', country: country.trim(), continent };
        const updatedCompanies = [...companies, newCompany];
        setCompanies(updatedCompanies);
        localStorage.setItem('fellowship_companies', JSON.stringify(updatedCompanies));
        const newDocs = { ...docs };
        DOCUMENT_TYPES.forEach(dt => {
          const key = `${newId}_${dt.id}`;
          const autoNA = getAutoNA(newCompany, dt);
          newDocs[key] = { status: autoNA ? 'na' : 'pending', link: '', notes: '', fileName: '', dateCollected: '' };
        });
        setDocs(newDocs);
        saveDocs(newDocs);
        const newActivity = [{ company: newCompany.name, doc: 'Company Registered', status: 'pending', ts: new Date().toISOString() }, ...activity.slice(0, 49)];
        setActivity(newActivity);
        logActivity({ company: newCompany.name, doc: 'Company Registered', status: 'pending' });
        setName(''); setCountry(''); setIndustry(''); setCustomSector(''); setIsCustomSector(false);
        setSuccessMsg(`Successfully added ${newCompany.name}!`);
        setTimeout(() => setSuccessMsg(''), 3000);
      }
    });
    return; // Stop sync execution
"""
    content = re.sub(r"    if \(!isEditMode\) \{\n      alert\(\"Please unlock Edit Mode to add companies\.\"\);\n      return;\n    \}\n    if \(prompt\(\"Enter master passcode to confirm adding this company:\"\) !== \"admin123\"\) \{\n      alert\(\"Incorrect passcode\.\"\);\n      return;\n    \}\n    if \(!name\.trim\(\) \|\| !country\.trim\(\)\) return;\n\n    const finalSector = isCustomSector \? customSector\.trim\(\) : sector;\n    if \(!finalSector\) return;\n\n    const newId = companies\.length > 0 \? Math\.max\(\.\.\.companies\.map\(c => c\.id\)\) \+ 1 : 1;\n    const newCompany = \{\n      id: newId,\n      name: name\.trim\(\),\n      sector: finalSector,\n      industry: industry\.trim\(\) \|\| 'General',\n      country: country\.trim\(\),\n      continent\n    \};\n\n    const updatedCompanies = \[\.\.\.companies, newCompany\];\n    setCompanies\(updatedCompanies\);\n    localStorage\.setItem\('fellowship_companies', JSON\.stringify\(updatedCompanies\)\);\n\n    // Initialize docs for new company\n    const newDocs = \{ \.\.\.docs \};\n    DOCUMENT_TYPES\.forEach\(dt => \{\n      const key = `\$\{newId\}_\$\{dt\.id\}`;\n      const autoNA = getAutoNA\(newCompany, dt\);\n      newDocs\[key\] = \{ status: autoNA \? 'na' : 'pending', link: '', notes: '', fileName: '', dateCollected: '' \};\n    \}\);\n    setDocs\(newDocs\);\n    saveDocs\(newDocs\);\n\n    // Log Activity\n    const newActivity = \[\{ company: newCompany\.name, doc: 'Company Registered', status: 'pending', ts: new Date\(\)\.toISOString\(\) \}, \.\.\.activity\.slice\(0, 49\)\];\n    setActivity\(newActivity\);\n    logActivity\(\{ company: newCompany\.name, doc: 'Company Registered', status: 'pending' \}\);\n\n    // Reset Form\n    setName\(''\);\n    setCountry\(''\);\n    setIndustry\(''\);\n    setCustomSector\(''\);\n    setIsCustomSector\(false\);\n\n    setSuccessMsg\(`Successfully added \$\{newCompany\.name\}!`\);\n    setTimeout\(\(\) => setSuccessMsg\(''\), 3000\);\n", new_add, content)

    # deleteCompany
    old_del = r"    if \(!isEditMode\) \{\n      alert\(\"Please unlock Edit Mode to delete companies\.\"\);\n      return;\n    \}\n    if \(prompt\(`Enter master passcode to confirm deletion of \$\{name\}:`\) !== \"admin123\"\) \{\n      alert\(\"Incorrect passcode\.\"\);\n      return;\n    \}\n    if \(!confirm\(`Are you sure you want to delete \$\{name\}\? This will clear all its documented URLs and notes\.`\)\) return;"
    new_del = """    if (!isEditMode) {
      window.showGlobalDialog({ type: 'alert', title: 'Edit Mode Locked', message: 'Please unlock Edit Mode to delete companies.' });
      return;
    }
    window.showGlobalDialog({
      type: 'prompt',
      title: 'Master Passcode',
      message: `Enter master passcode to confirm deletion of ${name}:`,
      confirmText: 'Verify',
      onConfirm: (val) => {
        if (val !== "admin123") {
          window.showGlobalDialog({ type: 'alert', title: 'Error', message: 'Incorrect passcode.', danger: true });
          return;
        }
        window.showGlobalDialog({
          type: 'confirm',
          title: 'Confirm Deletion',
          message: `Are you sure you want to delete ${name}? This will clear all its documented URLs and notes.`,
          danger: true,
          confirmText: 'Delete',
          onConfirm: () => {
             const updatedCompanies = companies.filter(c => c.id !== id);
             setCompanies(updatedCompanies);
             localStorage.setItem('fellowship_companies', JSON.stringify(updatedCompanies));
             const newDocs = { ...docs };
             DOCUMENT_TYPES.forEach(dt => { delete newDocs[`${id}_${dt.id}`]; });
             setDocs(newDocs); saveDocs(newDocs);
             const newActivity = [{ company: name, doc: 'Company Removed', status: 'na', ts: new Date().toISOString() }, ...activity.slice(0, 49)];
             setActivity(newActivity); logActivity({ company: name, doc: 'Company Removed', status: 'na' });
             setSelectedIds(prev => prev.filter(x => x !== id));
          }
        });
      }
    });
    return; // Stop sync execution"""
    content = re.sub(old_del + r".*?setSelectedIds\(prev => prev\.filter\(x => x !== id\)\);\n", new_del + "\n", content, flags=re.DOTALL)

    # deleteSelected
    old_del_sel = r"    if \(!isEditMode\) \{\n      alert\(\"Please unlock Edit Mode to delete companies\.\"\);\n      return;\n    \}\n    if \(selectedIds\.length === 0\) return;\n    if \(prompt\(`Enter master passcode to confirm deletion of \$\{selectedIds\.length\} companies:`\) !== \"admin123\"\) \{\n      alert\(\"Incorrect passcode\.\"\);\n      return;\n    \}\n    if \(!confirm\(`Are you sure you want to delete the \$\{selectedIds\.length\} selected companies\? This will permanently wipe their documented files and notes!`\)\) return;"
    new_del_sel = """    if (!isEditMode) {
      window.showGlobalDialog({ type: 'alert', title: 'Edit Mode Locked', message: 'Please unlock Edit Mode to delete companies.' });
      return;
    }
    if (selectedIds.length === 0) return;
    window.showGlobalDialog({
      type: 'prompt',
      title: 'Master Passcode',
      message: `Enter master passcode to confirm deletion of ${selectedIds.length} companies:`,
      confirmText: 'Verify',
      onConfirm: (val) => {
        if (val !== "admin123") {
          window.showGlobalDialog({ type: 'alert', title: 'Error', message: 'Incorrect passcode.', danger: true });
          return;
        }
        window.showGlobalDialog({
          type: 'confirm',
          title: 'Confirm Bulk Deletion',
          message: `Are you sure you want to delete the ${selectedIds.length} selected companies? This will permanently wipe their documented files and notes!`,
          danger: true,
          confirmText: 'Delete All Selected',
          onConfirm: () => {
             const updatedCompanies = companies.filter(c => !selectedIds.includes(c.id));
             setCompanies(updatedCompanies);
             localStorage.setItem('fellowship_companies', JSON.stringify(updatedCompanies));
             const newDocs = { ...docs };
             selectedIds.forEach(id => { DOCUMENT_TYPES.forEach(dt => { delete newDocs[`${id}_${dt.id}`]; }); });
             setDocs(newDocs); saveDocs(newDocs);
             const newActivity = [{ company: `${selectedIds.length} Companies`, doc: 'Batch Removed', status: 'na', ts: new Date().toISOString() }, ...activity.slice(0, 49)];
             setActivity(newActivity); logActivity({ company: `${selectedIds.length} Companies`, doc: 'Batch Removed', status: 'na' });
             setSelectedIds([]);
             setSuccessMsg(`Successfully deleted ${selectedIds.length} companies!`);
             setTimeout(() => setSuccessMsg(''), 3000);
          }
        });
      }
    });
    return; // Stop sync execution"""
    content = re.sub(old_del_sel + r".*?setTimeout\(\(\) => setSuccessMsg\(''\), 3000\);\n", new_del_sel + "\n", content, flags=re.DOTALL)


    # deleteAll
    old_del_all = r"    if \(!isEditMode\) \{\n      alert\(\"Please unlock Edit Mode to delete companies\.\"\);\n      return;\n    \}\n    if \(prompt\(\"Enter master passcode to confirm deleting ALL companies:\"\) !== \"admin123\"\) \{\n      alert\(\"Incorrect passcode\.\"\);\n      return;\n    \}\n    if \(!confirm\(`⚠️ DANGER ZONE! ⚠️\\n\\nAre you sure you want to delete ALL \$\{companies\.length\} companies\? This will completely empty your active research portfolio and delete all progress! This action CANNOT be undone\.`\)\) return;"
    new_del_all = """    if (!isEditMode) {
      window.showGlobalDialog({ type: 'alert', title: 'Edit Mode Locked', message: 'Please unlock Edit Mode to delete companies.' });
      return;
    }
    window.showGlobalDialog({
      type: 'prompt',
      title: 'Master Passcode',
      message: 'Enter master passcode to confirm deleting ALL companies:',
      confirmText: 'Verify',
      onConfirm: (val) => {
        if (val !== "admin123") {
          window.showGlobalDialog({ type: 'alert', title: 'Error', message: 'Incorrect passcode.', danger: true });
          return;
        }
        window.showGlobalDialog({
          type: 'confirm',
          title: '⚠️ DANGER ZONE! ⚠️',
          message: `Are you sure you want to delete ALL ${companies.length} companies?\n\nThis will completely empty your active research portfolio and delete all progress! This action CANNOT be undone.`,
          danger: true,
          confirmText: 'Wipe Everything',
          onConfirm: () => {
             setCompanies([]);
             localStorage.setItem('fellowship_companies', JSON.stringify([]));
             const newDocs = {}; setDocs(newDocs); saveDocs(newDocs);
             const newActivity = [{ company: 'Full Portfolio', doc: 'Wiped Clean', status: 'na', ts: new Date().toISOString() }, ...activity.slice(0, 49)];
             setActivity(newActivity); logActivity({ company: 'Full Portfolio', doc: 'Wiped Clean', status: 'na' });
             setSelectedIds([]);
             setSuccessMsg('Active research portfolio wiped clean.');
             setTimeout(() => setSuccessMsg(''), 3000);
          }
        });
      }
    });
    return; // Stop sync execution"""
    content = re.sub(old_del_all + r".*?setTimeout\(\(\) => setSuccessMsg\(''\), 3000\);\n", new_del_all + "\n", content, flags=re.DOTALL)


    # resetToDefault
    old_res = r"    if \(!isEditMode\) \{\n      alert\(\"Please unlock Edit Mode to reset data\.\"\);\n      return;\n    \}\n    if \(prompt\(\"Enter master passcode to confirm factory reset:\"\) !== \"admin123\"\) \{\n      alert\(\"Incorrect passcode\.\"\);\n      return;\n    \}\n    if \(!confirm\('Revert portfolio to the original 100 benchmark companies\? This will delete all custom companies added\.'\)\) return;"
    new_res = """    if (!isEditMode) {
      window.showGlobalDialog({ type: 'alert', title: 'Edit Mode Locked', message: 'Please unlock Edit Mode to reset data.' });
      return;
    }
    window.showGlobalDialog({
      type: 'prompt',
      title: 'Master Passcode',
      message: 'Enter master passcode to confirm factory reset:',
      confirmText: 'Verify',
      onConfirm: (val) => {
        if (val !== "admin123") {
          window.showGlobalDialog({ type: 'alert', title: 'Error', message: 'Incorrect passcode.', danger: true });
          return;
        }
        window.showGlobalDialog({
          type: 'confirm',
          title: 'Confirm Factory Reset',
          message: 'Revert portfolio to the original 100 benchmark companies? This will delete all custom companies added.',
          danger: true,
          confirmText: 'Reset to Default',
          onConfirm: () => {
             setCompanies(DEFAULT_COMPANIES);
             localStorage.removeItem('fellowship_companies');
             const newDocs = initDocs(DEFAULT_COMPANIES);
             setDocs(newDocs); saveDocs(newDocs);
             window.location.reload();
          }
        });
      }
    });
    return; // Stop sync execution"""
    content = re.sub(old_res + r".*?window\.location\.reload\(\);\n", new_res + "\n", content, flags=re.DOTALL)


    # handleFileUpload
    old_file = r"    if \(!isEditMode\) \{\n      alert\(\"Please unlock Edit Mode to import companies\.\"\);\n      e\.target\.value = null;\n      return;\n    \}\n    if \(prompt\(\"Enter master passcode to confirm importing companies:\"\) !== \"admin123\"\) \{\n      alert\(\"Incorrect passcode\.\"\);\n      e\.target\.value = null;\n      return;\n    \}"
    new_file = """    if (!isEditMode) {
      window.showGlobalDialog({ type: 'alert', title: 'Edit Mode Locked', message: 'Please unlock Edit Mode to import companies.' });
      e.target.value = null;
      return;
    }
    const file = e.target.files[0];
    if (!file) return;

    window.showGlobalDialog({
      type: 'prompt',
      title: 'Master Passcode',
      message: 'Enter master passcode to confirm importing companies from ' + file.name + ':',
      confirmText: 'Verify & Import',
      onConfirm: (val) => {
        if (val !== "admin123") {
          window.showGlobalDialog({ type: 'alert', title: 'Error', message: 'Incorrect passcode.', danger: true });
          e.target.value = null;
          return;
        }
        
        // Execute original file reader logic
        const ext = file.name.split('.').pop().toLowerCase();
        const reader = new FileReader();

        reader.onload = (ev) => {
          let rows = [];
          try {
            if (ext === 'csv') {
              const text = ev.target.result;
              const parsed = Papa.parse(text, { header: true, skipEmptyLines: true });
              rows = parsed.data;
            } else if (['xlsx', 'xls'].includes(ext)) {
              const data = new Uint8Array(ev.target.result);
              const workbook = XLSX.read(data, { type: 'array' });
              const sheetName = workbook.SheetNames[0];
              const sheet = workbook.Sheets[sheetName];
              rows = XLSX.utils.sheet_to_json(sheet);
            } else {
              window.showGlobalDialog({ type: 'alert', title: 'Error', message: 'Unsupported file format. Please upload .xlsx, .xls, or .csv', danger: true });
              return;
            }

            if (rows.length === 0) {
              window.showGlobalDialog({ type: 'alert', title: 'Error', message: 'No data found in the uploaded file.', danger: true });
              return;
            }

            let importedCount = 0;
            const newCompanies = [...companies];
            const newDocs = { ...docs };
            const newActivities = [...activity];
            let nextId = newCompanies.length > 0 ? Math.max(...newCompanies.map(c => c.id)) + 1 : 1;

            rows.forEach(row => {
              const normalized = {};
              Object.keys(row).forEach(k => {
                const kl = k.toLowerCase().trim();
                if (['company', 'name', 'company name'].includes(kl)) normalized.name = row[k];
                else if (['country', 'region (country)', 'region'].includes(kl)) normalized.country = row[k];
                else if (kl === 'sector') normalized.sector = row[k];
                else if (kl === 'industry') normalized.industry = row[k];
                else if (kl === 'continent') normalized.continent = row[k];
              });
              if (!normalized.name || !String(normalized.name).trim()) return;
              const companyName = String(normalized.name).trim();
              if (newCompanies.some(c => c.name.toLowerCase() === companyName.toLowerCase())) return;

              const compObj = { id: nextId, name: companyName, sector: String(normalized.sector || 'Industrials').trim(), industry: String(normalized.industry || 'General').trim(), country: String(normalized.country || 'United States').trim(), continent: String(normalized.continent || 'North America').trim() };
              newCompanies.push(compObj);
              DOCUMENT_TYPES.forEach(dt => {
                const autoNA = getAutoNA(compObj, dt);
                newDocs[`${nextId}_${dt.id}`] = { status: autoNA ? 'na' : 'pending', link: '', notes: '', fileName: '', dateCollected: '' };
              });
              newActivities.unshift({ company: companyName, doc: 'Company Imported', status: 'pending', ts: new Date().toISOString() });
              nextId++; importedCount++;
            });

            if (importedCount > 0) {
              setCompanies(newCompanies); localStorage.setItem('fellowship_companies', JSON.stringify(newCompanies));
              setDocs(newDocs); saveDocs(newDocs);
              setActivity(newActivities.slice(0, 50)); localStorage.setItem(ACTIVITY_KEY, JSON.stringify(newActivities.slice(0, 50)));
              setSuccessMsg(`Successfully imported ${importedCount} companies from ${file.name}!`);
              setTimeout(() => setSuccessMsg(''), 4000);
            } else {
              window.showGlobalDialog({ type: 'alert', title: 'Import Failed', message: 'No new unique companies could be parsed. Make sure column headers are named Name/Company, Country, Sector, Industry, or Continent.', danger: true });
            }
          } catch (err) {
            console.error(err);
            window.showGlobalDialog({ type: 'alert', title: 'Error', message: 'Error parsing file: ' + err.message, danger: true });
          }
        };
        if (ext === 'csv') reader.readAsText(file); else reader.readAsArrayBuffer(file);
      }
    });
    
    e.target.value = ''; // Reset input
    return; // Stop sync execution"""
    content = re.sub(old_file + r".*?e\.target\.value = ''; // Reset input\n  \}", new_file + "\n  }", content, flags=re.DOTALL)


    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    main()
