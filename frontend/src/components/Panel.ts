export abstract class Panel {
  protected el: HTMLElement;
  protected collapsed = false;

  constructor(protected container: HTMLElement, protected title: string) {
    this.el = document.createElement('div');
    this.el.className = 'panel';
    this.el.innerHTML = `
      <div class="panel-header">
        <span class="panel-title">${title}</span>
        <button class="panel-toggle">\u2212</button>
      </div>
      <div class="panel-body"></div>
    `;

    this.el.querySelector('.panel-toggle')!.addEventListener('click', () => {
      this.collapsed = !this.collapsed;
      this.el.querySelector('.panel-body')!.classList.toggle('hidden', this.collapsed);
      this.el.querySelector('.panel-toggle')!.textContent = this.collapsed ? '+' : '\u2212';
    });

    this.container.appendChild(this.el);
  }

  protected get body(): HTMLElement {
    return this.el.querySelector('.panel-body')!;
  }

  abstract update(data: unknown): void;

  destroy(): void {
    this.el.remove();
  }
}
