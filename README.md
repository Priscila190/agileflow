# 📌 AgileFlow – Sistema Ágil de Gerenciamento de Tarefas

## 📖 Descrição do Projeto

O **AgileFlow** é um sistema de gerenciamento de tarefas e compromissos desenvolvido como parte de uma simulação prática de Engenharia de Software.
Inspirado em metodologias ágeis, o projeto busca fornecer um ambiente simples e eficiente para:

* Agendamento de compromissos.
* Registro e autenticação de usuários.
* Acompanhamento de atividades em tempo real.
* Organização do fluxo de trabalho usando **Kanban** [GitHub Projects](https://github.com/users/Priscila190/projects/3)

Este repositório foi planejado para demonstrar não apenas a implementação do software, mas também a aplicação de **boas práticas de documentação, controle de qualidade e gestão de mudanças**.

---

## 🎯 Objetivos

* Criar um **sistema funcional** de login e gerenciamento de tarefas/compromissos.
* Aplicar conceitos de **Scrum e Kanban** no ciclo de vida do software.
* Demonstrar o uso de **controle de qualidade** via testes automatizados e GitHub Actions.
* Simular a **gestão de mudanças**, registrando alterações no escopo do projeto.

---

## 🛠️ Metodologia Adotada

* **Kanban**: Utilizado no GitHub Projects, com colunas **A Fazer**, **Em Progresso** e **Concluído**.
* **SCRUM**: As tarefas foram divididas em pequenos incrementos simulando *sprints* curtos.
* **Commits Semânticos**: Padrão adotado para manter histórico de mudanças claro e objetivo.

---

## ⚙️ Funcionalidades

* ✅ Cadastro e autenticação de usuários (com senha criptografada).
* ✅ CRUD de compromissos: criar, listar, atualizar e excluir.
* ✅ Listagem de compromissos por status:
    * Próximos.
    * De hoje.
    * Expirados.
* ✅ Controle de sessão e permissões com `login_required`.
* ✅ Validação e sanitização de dados de entrada.


---

## ▶️ Como Executar o Projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/Priscila190/agileflow.git
cd agileflow
```

### 2. Criar ambiente virtual e instalar dependências

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

### 3. Executar aplicação

```bash
flask run or python app.py
```

O sistema estará disponível em: **[http://localhost:3001](http://localhost:3001)**

---


## 🔄 Gestão de Mudanças

Durante o desenvolvimento, foi adicionada a funcionalidade de **notificação de compromissos próximos**.

* Justificativa: feedback do cliente solicitando maior visibilidade para compromissos urgentes.
* Alterações realizadas:

    * Atualização do modelo `Appointment`.
    * Implementação de filtros para compromissos próximos (até 30 min).
    * Registro da mudança no **Kanban**.

---

## 📌 Requisitos

### Funcionais

* RF01 – O sistema deve permitir cadastro e autenticação de usuários.
* RF02 – O sistema deve permitir CRUD de compromissos.
* RF03 – O sistema deve listar compromissos por status (próximos, de hoje e expirados).



## 👥 Beneficiados

* **Equipes ágeis**: acompanham fluxo de trabalho.
* **Gestores**: monitoram compromissos e produtividade.
* **Usuários finais**: gerenciam atividades e horários de forma simples e clara.

---

## 📌 Tecnologias Utilizadas

* **Backend**: Python (Flask).
* **Banco de Dados**: SQLite (padrão) – adaptável para PostgreSQL.


---

