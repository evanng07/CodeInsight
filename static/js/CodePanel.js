export default class CodePanel {
    static panelCount = 0; // Track the number of open panels

    constructor() {
      this.panel = document.createElement("div");
      this.panel.id = "code-panel";
      this.panel.style.position = "absolute";
      this.panel.style.top = "10px";
      this.panel.style.right = "10px";
      this.panel.style.width = "35%";
      this.panel.style.height = "80%";
      this.panel.style.overflowY = "auto";
      this.panel.style.background = "#1e1e1e";
      this.panel.style.border = "1px solid #333";
      this.panel.style.padding = "10px";
      this.panel.style.fontFamily = `"Courier New", Courier, monospace`;
      this.panel.style.boxShadow = "0 2px 5px rgba(0,0,0,0.7)";
      this.panel.style.zIndex = "10";
      this.panel.style.display = "none"; // initially hidden
  
      // Create a header for metadata and controls.
      this.metadata = document.createElement("div");
      this.metadata.className = "metadata";
      this.panel.appendChild(this.metadata);
  
      // Create a container for the code.
      this.pre = document.createElement("pre");
      this.codeEl = document.createElement("code");
      this.codeEl.className = "python"; // for syntax highlighting
      this.pre.appendChild(this.codeEl);
      this.panel.appendChild(this.pre);
  
      // Optionally, add a close/minimize button.
      this.closeBtn = document.createElement("button");
      this.closeBtn.textContent = "Close";
      this.closeBtn.style.position = "absolute";
      this.closeBtn.style.top = "5px";
      this.closeBtn.style.right = "5px";
      this.closeBtn.addEventListener("click", () => this.hide());
      this.panel.appendChild(this.closeBtn);
  
      // Add this in the constructor after creating the close button
      this.analyzeBtn = document.createElement("button");
      this.analyzeBtn.textContent = "Analyze";
      this.analyzeBtn.style.position = "absolute";
      this.analyzeBtn.style.top = "5px";
      this.analyzeBtn.style.right = "60px"; // Adjust position to the left of the close button
      this.analyzeBtn.addEventListener("click", () => this.analyze());
      this.panel.appendChild(this.analyzeBtn);
  
      this.setPosition(); // Set the position when the panel is created
      document.body.appendChild(this.panel);
    }
  
    setPosition() {
      const offset = 30; // Offset for each new panel
      const x = 10 + (CodePanel.panelCount * offset); // Calculate new x position
      const y = 10; // Keep y position constant
      this.panel.style.top = `${y}px`;
      this.panel.style.right = `${x}px`;
      CodePanel.panelCount++; // Increment the panel count
    }
  
    // Method to open the panel with given details.
    open(details) {
      this.metadata.innerHTML = `
        <strong>File:</strong> ${details.file}<br>
        <strong>Path:</strong> ${details.breadcrumbs}<br>
        <strong>Function:</strong> ${details.id}
      `;
      this.codeEl.textContent = details.code;
      // Call Highlight.js on the new code element.
      if (window.hljs) {
        hljs.highlightElement(this.codeEl);
      }
      this.show();
    }
  
    show() {
      this.panel.style.display = "block";
    }
  
    hide() {
      CodePanel.panelCount--; // Decrement the panel count when hiding
      this.panel.style.display = "none";
    }
  
    analyze() {
      const functionName = this.metadata.querySelector("strong:nth-child(3)").nextSibling.textContent.trim(); // Get the function name
      const question = `How does this ${functionName} work?`;
      
      // Send the question to the Flask app
      fetch('/chatbot', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({ query: question })
      })
      .then(response => response.json())
      .then(data => {
          // Handle the response from the chatbot
          const chatbotResponse = data.response;
          // Display the response in the chatbot content area
          const chatbotContent = document.getElementById("chatbot-content");
          const messageElement = document.createElement("div");
          messageElement.textContent = chatbotResponse;
          messageElement.classList.add("bot-message");
          chatbotContent.appendChild(messageElement);
          chatbotContent.scrollTop = chatbotContent.scrollHeight; // Scroll to the bottom
      })
      .catch(error => {
          console.error('Error:', error);
      });
    }
  
    // Optionally, add methods to minimize, resize, etc.
  }
  