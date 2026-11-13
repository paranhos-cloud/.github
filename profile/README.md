<div align="center">

<a href="https://paranhos.cloud"><img src="assets/hero.svg" width="100%" alt="Paranhos Cloud — Seu projeto. Online em minutos. Hospede sites e aplicações sem configurar infraestrutura." /></a>

<br />

<a href="https://app.paranhos.cloud/signup"><img src="assets/btn-start.svg" height="46" alt="Começar grátis" /></a>&nbsp;
<a href="https://docs.paranhos.cloud"><picture><source media="(prefers-color-scheme: light)" srcset="assets/btn-docs-light.svg" /><img src="assets/btn-docs-dark.svg" height="46" alt="Documentação" /></picture></a>&nbsp;
<a href="https://paranhos.cloud"><picture><source media="(prefers-color-scheme: light)" srcset="assets/btn-site-light.svg" /><img src="assets/btn-site-dark.svg" height="46" alt="Site" /></picture></a>&nbsp;
<a href="https://status.paranhos.cloud"><picture><source media="(prefers-color-scheme: light)" srcset="assets/btn-status-light.svg" /><img src="assets/btn-status-dark.svg" height="46" alt="Status" /></picture></a>

<br /><br />

<picture>
  <source media="(prefers-color-scheme: light)" srcset="assets/how-light.svg" />
  <img src="assets/how-dark.svg" width="100%" alt="Como funciona: conecte o repositório, o build roda no seu GitHub Actions e o site fica no ar com HTTPS." />
</picture>

</div>

<br />

Um pull request adiciona o workflow ao seu repositório. Depois disso, cada push na `main` faz o build no seu próprio GitHub Actions e só a pasta final sobe para a Paranhos Cloud:

```yaml
permissions:
  contents: read
  id-token: write   # GitHub OIDC: nenhum segredo guardado no repositório

steps:
  - uses: actions/checkout@v7
  - uses: paranhos-cloud/deploy-action@v1
```

### Código aberto

<a href="https://github.com/paranhos-cloud/deploy-action"><picture><source media="(prefers-color-scheme: light)" srcset="assets/repo-deploy-action-light.svg" /><img src="assets/repo-deploy-action-dark.svg" width="49%" alt="deploy-action" /></picture></a>
<a href="https://github.com/paranhos-cloud/docs"><picture><source media="(prefers-color-scheme: light)" srcset="assets/repo-docs-light.svg" /><img src="assets/repo-docs-dark.svg" width="49%" alt="docs" /></picture></a>

<br />

<a href="https://paranhos.cloud"><img src="assets/footer.svg" width="100%" alt="Paranhos Cloud — feito no Brasil" /></a>
