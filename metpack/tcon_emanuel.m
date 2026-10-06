function E = tcon_emanuel(pasta, titulo, corte)
% TCON_EMANUEL  Executa o programa de Kerry Emanuel (wyoming.f) para a sondagem em PASTA
% e desenha as matrizes de flutuabilidade (diferença de temperatura de densidade
% parcela - ambiente) para a ascensão reversível e a pseudoadiabática.
%
% Adaptado de tcon.m (K. Emanuel, https://texmex.mit.edu/pub/emanuel/soundings/).
% Diferenças em relação ao original:
%   - compila o wyoming.f automaticamente (gfortran), se houver compilador;
%   - CORTE = false (padrão) remove o piso artificial de -4 K do wyoming.f original,
%     como no notebook Seminario_plot_sounding_revisado.ipynb;
%   - as duas matrizes ficam lado a lado, com a mesma escala de cores, isolinha de 0 K
%     destacada e eixo vertical até 100 hPa.
%
% Uso:
%   E = tcon_emanuel('emanuel_19951224_12', 'INSTÁVEL 24/12/1995 12Z');
%
% PASTA deve conter o sounding.txt gravado por getsounding_wyoming.m.
% Sem compilador Fortran (por exemplo, se o MATLAB Online não tiver gfortran), copie para PASTA
% os arquivos p.out, porig.out, tdifrev.out, tdifpseudo.out e cape.out gerados pelo notebook
% (pastas emanuel_AAAAMMDD_HH) e chame tcon_emanuel novamente: os arquivos existentes são usados.

if nargin < 2 || isempty(titulo), titulo = pasta; end
if nargin < 3, corte = false; end

saidas = {'p.out', 'porig.out', 'tdifrev.out', 'tdifpseudo.out', 'cape.out'};
exe = prepara_wyoming(corte);
if ~isempty(exe)
    dir_ant = pwd;
    cd(pasta);
    [st, msg] = system(['"' exe '"']);
    cd(dir_ant);
    if st ~= 0
        error('wyoming.f falhou na pasta %s:\n%s', pasta, msg);
    end
end
for k = 1:numel(saidas)
    if ~exist(fullfile(pasta, saidas{k}), 'file')
        error(['%s não encontrado em %s. Sem compilador Fortran, copie para essa pasta os arquivos ' ...
               'p.out, porig.out, tdifrev.out, tdifpseudo.out e cape.out gerados pelo notebook.'], saidas{k}, pasta);
    end
end

E.p = load(fullfile(pasta, 'p.out'));
E.porig = load(fullfile(pasta, 'porig.out'));
E.rev = load(fullfile(pasta, 'tdifrev.out'));
E.pse = load(fullfile(pasta, 'tdifpseudo.out'));
E.cape = le_cape_out(fullfile(pasta, 'cape.out'));
[X, Y] = meshgrid(E.porig(:)', E.p(:));
E.X = X; E.Y = Y;

% escala simétrica comum: pelo menos +-6 K, em passos pares, pela maior flutuabilidade positiva
vis = (Y < X) & (Y >= 100);
amp = max(6, 2 * ceil(max([E.rev(vis); E.pse(vis)]) / 2));
cmap = [linspace(0.02, 1, 32)', linspace(0.19, 1, 32)', linspace(0.38, 1, 32)'; ...
        linspace(1, 0.40, 32)', linspace(1, 0, 32)', linspace(1, 0.05, 32)'];

figure('Name', ['Emanuel - ' titulo], 'Color', 'w', 'Position', [50 50 1300 600]);
campos = {E.rev, E.pse};
nomes = {'Ascensão reversível', 'Ascensão pseudoadiabática'};
colunas = [6 7];   % CAPE reversível e pseudoadiabática em cape.out
for i = 1:2
    subplot(1, 2, i);
    Z = campos{i};
    Z(Y >= X) = NaN;                       % só níveis acima do nível de origem
    pcolor(X, Y, Z); shading interp; hold on
    niveis = -amp:2:amp; niveis(niveis == 0) = [];
    [c, h] = contour(X, Y, Z, niveis, 'k'); clabel(c, h, 'FontSize', 8);
    contour(X, Y, Z, [0 0], 'k', 'LineWidth', 2);
    hold off
    colormap(cmap); caxis([-amp amp]);
    set(gca, 'YDir', 'reverse', 'XDir', 'reverse', 'FontWeight', 'bold', 'Layer', 'top');
    ylim([100 max(E.p)]);
    xlabel('Pressão de origem da parcela (hPa)');
    ylabel('Pressão para a qual a parcela é elevada (hPa)');
    [cmax, kmax] = max(E.cape(:, colunas(i)));
    title({nomes{i}, sprintf('CAPE máx: %.0f J/kg (origem %.0f hPa)', cmax, E.cape(kmax, 1))});
end
cb = colorbar('southoutside');
xlabel(cb, 'Diferença de temperatura de densidade parcela - ambiente (K)');
if exist('sgtitle', 'file')
    sgtitle(['Matrizes de flutuabilidade de Emanuel - ' titulo], 'FontWeight', 'bold');
end
end

function exe = prepara_wyoming(corte)
% Compila o wyoming.f (uma vez). Devolve '' se não houver compilador.
pasta_m = fileparts(mfilename('fullpath'));
if ispc
    exe = fullfile(pasta_m, 'wyoming_emanuel.exe');
else
    exe = fullfile(pasta_m, 'wyoming_emanuel');
end
fonte = fullfile(pasta_m, 'wyoming.f');
codigo = fileread(fonte);
if ~corte
    codigo = strrep(codigo, 'TRDBAR(I,J)=MAX(TRDBAR(I,J),-4.0)', 'CONTINUE');
    codigo = strrep(codigo, 'TPDBAR(I,J)=MAX(TPDBAR(I,J),-4.0)', 'CONTINUE');
end
usado = fullfile(pasta_m, 'wyoming_usado.f');
fid = fopen(usado, 'w'); fprintf(fid, '%s', codigo); fclose(fid);
[st, ~] = system(sprintf('gfortran -O2 -o "%s" "%s"', exe, usado));
if st ~= 0
    fprintf(['Aviso: não foi possível compilar o wyoming.f (gfortran ausente?). ' ...
             'Serão usados os arquivos .out já existentes na pasta da sondagem.\n']);
    exe = '';
end
end

function C = le_cape_out(arq)
% Lê as linhas numéricas de cape.out:
% origem, PA_rev, PA_pse, NA_rev, NA_pse, CAPE_rev, CAPE_pse, DCAPE
txt = regexp(fileread(arq), '\r?\n', 'split');
C = [];
for k = 1:numel(txt)
    if ~isempty(regexp(txt{k}, '^\s*-?\d+\.\d', 'once'))
        v = sscanf(txt{k}, '%f')';
        if numel(v) >= 8
            C = [C; v(1:8)]; %#ok<AGROW>
        end
    end
end
end
