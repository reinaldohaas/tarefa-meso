# Pacote `metpack`: Diagnóstico Termodinâmico e Cinemático de Mesoescala
**Disciplina:** Meteorologia de Mesoescala (FSC7116 - UFSC)  
**Autor:** Reinaldo Haas  
**Fundamentação Teórica:** Kerry Emanuel (1994, *Atmospheric Convection*, Oxford University Press) e MIT OpenCourseWare (12.811 - *Atmospheric Convection*).

---

## 0. Diretriz Didática para os Alunos

Cada aluno ou dupla escolhe **três radiossondagens próprias** (datas e/ou estações diferentes das do exemplo), uma para cada regime: estável, neutro e instável. Os casos de Porto Alegre (SBPA 83971) em 12/12, 22/12 e 24/12/1995 são apenas o exemplo resolvido. Veja `ROTEIRO_ESTUDANTES.md`.

---

## 1. Conteúdo da pasta

Programas de Kerry Emanuel ([texmex.mit.edu/pub/emanuel/soundings](https://texmex.mit.edu/pub/emanuel/soundings/)) adaptados à interface atual do Wyoming, em MATLAB e em Python, com os mesmos nomes e os mesmos passos:

| Original (Emanuel) | MATLAB | Python | Função |
| :--- | :--- | :--- | :--- |
| `getsounding.m` | `getsounding_wyoming.m` | `getsounding_wyoming.py` | Baixa a sondagem do Wyoming (wsgi), converte o vento para nós e grava `sounding.txt`, `header.txt` e `modsound.txt` no formato do `wyoming.f`. |
| `wyoming.f` | `wyoming_emanuel.m` (tradução, sem Fortran) | `wyoming.f` (compilado com gfortran) | Ascensão de parcelas reversível e pseudoadiabática: gera `cape.out`, `p.out`, `porig.out`, `tdifrev.out` e `tdifpseudo.out`. |
| `tcon.m` | `tcon_emanuel.m` | `tcon_emanuel.py` | Calcula (MATLAB: `wyoming_emanuel.m`; Python: `wyoming.f`) e desenha as matrizes de flutuabilidade, sem o piso artificial de −4 K. |
| `skewt.m` | `skewt.m` | `skewt.py` | Diagrama Skew-T de Emanuel: `skewt(p, T, UR 0-1)`. |
| — | `tarefa_sondagens.m` | `tarefa_sondagens.py` | Script principal: roda as três sondagens de `CASOS`. |

Os arquivos `getsounding.m` e `tcon.m` são os originais de Emanuel, mantidos só como referência (o endereço do Wyoming que eles usam não existe mais).

Outros arquivos:
- `calc_metricas.py`, `metricas.json`, `metricas_notebook.json`: valores do exemplo usados pelo site e pelos slides (vêm do notebook `Seminario_plot_sounding_revisado.ipynb`).
- `sounding_AAAAMMDD_12Z.txt` e `indices_AAAAMMDD_12Z.txt`: cópias das páginas do Wyoming para os três casos do exemplo (usadas quando o Wyoming não responde).
- `*.png`: figuras do site e dos slides.
- `mapas/`: contornos do Natural Earth para os mapas.
- Rotinas auxiliares de termodinâmica em MATLAB (`thermo_*.m`, `brunt_*.m`, `theta_*.m`, `convert_humidity/` etc.), descritas em `Leiame.txt`.

---

## 2. Fundamentos Físico-Matemáticos de Kerry Emanuel (1994)

### 2.1. Temperatura Virtual ($T_v$) vs. Temperatura de Densidade ($T_\rho$)
Na aproximação pseudoadiabática clássica, assume-se que toda a água condensada precipita instantaneamente ($r_l = 0$):
$$T_v = T \left( \frac{1 + \frac{r_v}{\epsilon}}{1 + r_v} \right) \approx T(1 + 0.608\, r_v)$$

No entanto, Kerry Emanuel (1994, Seções 4.3 e 6.3) demonstra que na ascensão real a nuvem retém condensado. A **Temperatura de Densidade ($T_\rho$)** contabiliza o peso gravitacional da água líquida (*water loading*):
$$T_\rho = T \left( \frac{1 + \frac{r_v}{\epsilon}}{1 + r_t} \right) \approx T(1 + 0.608\, r_v - r_l - r_i)$$
onde $r_t$ é a razão de mistura de água total conservada ($r_t = r_{\text{origem}}$) e $r_l = r_t - r_{vs}(T, p)$.

### 2.2. Flutuabilidade e CAPE
$$B = g \left( \frac{T_{\rho, p} - T_{\rho, e}}{T_{\rho, e}} \right)$$

$$\text{CAPE} = \int_{p_{\text{EL}}}^{p_{\text{LFC}}} R_d (T_{\rho, p} - T_{\rho, e})\, d\ln p$$

Em ambientes tropicais ou subtropicais quentes e úmidos, o termo $-r_l$ (retenção de água líquida) reduz expressivamente a flutuabilidade e o CAPE efetivo em relação ao cálculo pseudoadiabático convencional. Todos os valores comparativos para as 3 sondagens são calculados dinamicamente e consolidados em `metricas.json`.

---

## 3. Como rodar

**Python** (com o uv; precisa do `gfortran` para o `wyoming.f`), na pasta do repositório:
```powershell
uv run --with numpy --with matplotlib python metpack/tarefa_sondagens.py
```
Para cada caso de `CASOS`, a pasta `emanuel_AAAAMMDD_HH` recebe `skewt.png`, `matrizes_emanuel.png` e as saídas do `wyoming.f`.

**MATLAB Online**: envie a pasta `metpack/` para o MATLAB Drive, abra `tarefa_sondagens.m`, troque `CASOS` e clique em Run.

**Notebook** (índices do MetPy, perfis, hodógrafo e figuras do site): `Seminario_plot_sounding_revisado.ipynb`. Depois dele, `calc_metricas.py`, `generate_figures.py`, `build_index_html.py` e `generate_pptx.py` atualizam o site e os slides (ver `README.md` na raiz).

---

## 4. Saídas do `wyoming.f`

* **`cape.out`**: para cada nível de origem, área positiva e negativa (reversível e pseudoadiabática), CAPE reversível, CAPE pseudoadiabática e DCAPE.
* **`p.out`**: níveis de pressão para os quais a parcela é elevada.
* **`porig.out`**: níveis de pressão de origem da parcela.
* **`tdifrev.out`**: matriz de diferença de temperatura de densidade parcela − ambiente, ascensão reversível (K).
* **`tdifpseudo.out`**: a mesma matriz para a ascensão pseudoadiabática (K).
* **`modsound.txt`**: perfil usado (P, T, UR).
