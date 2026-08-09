document.getElementById('run-btn').addEventListener('click', async () => {
    const code = document.getElementById('code-editor').value;
    const outputTerminal = document.getElementById('output-terminal');
    
    outputTerminal.innerText = "Compiling...\n";
    outputTerminal.style.color = "#f39c12"; 
    
    try {
        // Unga exact Render URL + /compile endpoint
        const backendURL = 'https://qpp-compiler.onrender.com/compile'; 
        
        const response = await fetch(backendURL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: code })
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
        outputTerminal.innerText = "Network Error: API is waking up or URL is unreachable. Please wait 1 minute and try again.";
    }
});
