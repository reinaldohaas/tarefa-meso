function E = tcon_emanuel(pasta, titulo, corte)
% TCON_EMANUEL  Calcula, para a sondagem em PASTA, as matrizes de flutuabilidade de Kerry Emanuel
% (diferença de temperatura de densidade parcela - ambiente) nas ascensões reversível e
% pseudoadiabática e desenha as duas lado a lado, como o tcon.m original.
%
% Adaptado de tcon.m (K. Emanuel, https://texmex.mit.edu/pub/emanuel/soundings/).
% O tcon.m original roda o executável wyoming.exe (Fortran); aqui o cálculo é feito pela
% tradução em MATLAB do wyoming.f (wyoming_emanuel.m), que dá os mesmos resultados
% (diferença < 0,001 K nas matrizes e < 0,1 J/kg na CAPE) e não precisa de compilador.
%   - CORTE = false (padrão) não aplica o piso artificial de -4 K do wyoming.f original;
%   - grava em PASTA os mesmos arquivos do wyoming.f: p.out, porig.out, tdifrev.out,
%     tdifpseudo.out e cape.out.
%
% Uso:
%   E = tcon_emanuel('emanuel_19951224_12', 'INSTÁVEL 24/12/1995 12Z');
% PASTA deve conter o sounding.txt gravado por getsounding_wyoming.m.

if nargin < 2 || isempty(titulo), titulo = pasta; end
if nargin < 3, corte = false; end

[E.p, E.porig, E.rev, E.pse, E.cape] = wyoming_emanuel(fullfile(pasta, 'sounding.txt'), corte);
grava_saidas(pasta, E);
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

function grava_saidas(pasta, E)
% Grava os arquivos de saída no mesmo formato do wyoming.f
fid = fopen(fullfile(pasta, 'p.out'), 'w');     fprintf(fid, '%9.3f\n', E.p);     fclose(fid);
fid = fopen(fullfile(pasta, 'porig.out'), 'w'); fprintf(fid, '%9.3f\n', E.porig); fclose(fid);
fmt = [repmat(' %7.3f', 1, size(E.rev, 2)) '\n'];
fid = fopen(fullfile(pasta, 'tdifrev.out'), 'w');    fprintf(fid, fmt, E.rev');  fclose(fid);
fid = fopen(fullfile(pasta, 'tdifpseudo.out'), 'w'); fprintf(fid, fmt, E.pse');  fclose(fid);
fid = fopen(fullfile(pasta, 'cape.out'), 'w');
fprintf(fid, '                    ALL AREAS IN UNITS OF J/kg\n\n');
fprintf(fid, ' Origin    Rev.    P.A.    Rev.    P.A.    Rev.    P.A.    Rev.\n');
fprintf(fid, ' p (mb)     PA      PA      NA      NA     CAPE    CAPE   DCAPE\n');
fprintf(fid, ' %6.1f%8.1f%8.1f%8.1f%8.1f%8.1f%8.1f%8.1f\n', E.cape');
fclose(fid);
end
