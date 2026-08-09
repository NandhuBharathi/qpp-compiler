document.getElementById('run-btn').addEventListener('click', async () => {
    const code = document.getElementById('code-editor').value;
    // 💥 Pudhusu: HTML-la irukka custom-input box-oda value-ah edukkurom
    const customInput = document.getElementById('custom-input') ? document.getElementById('custom-input').value : ""; 
    const outputTerminal = document.getElementById('output-terminal');
    
    outputTerminal.innerText = "Compiling...\n";
    outputTerminal.style.color = "#f39c12"; 
    
    try {
        // UNGA EXACT RENDER URL AH INGA POTUKONGA
        const backendURL = 'https://qpp-compiler.onrender.com/compile'; 
        
        const response = await fetch(backendURL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            // 💥 Pudhusu: code kooda input-aiyum serthu anuppurom
            body: JSON.stringify({ code: code, input: customInput }) 
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            outputTerminal.style.color = "#4af626";
            outputTerminal.innerText = data.output;
        } else {
            outputTerminal.style.color = "#ff4d4d";
            outputTerminal.innerText = "Compilation Error:\n" + (data.error || "Unknown error");
        }
    } catch (error) {
        outputTerminal.style.color = "#ff4d4d";
        outputTerminal.innerText = "Network Error: Could not connect to Backend Engine.";
    }
});
