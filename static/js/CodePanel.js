export default class CodePanel {
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
  
      document.body.appendChild(this.panel);
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
      this.panel.style.display = "none";
    }
  
    // Optionally, add methods to minimize, resize, etc.
  }
  