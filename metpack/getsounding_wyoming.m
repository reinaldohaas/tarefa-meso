function [data, header, status, fonte] = getsounding_wyoming(station_id, year, month, day, hour, src)
% GETSOUNDING_WYOMING  Baixa uma radiossondagem do Wyoming (interface atual "wsgi") e
% prepara os arquivos de entrada do programa de Kerry Emanuel (wyoming.f).
%
% Adaptado de getsounding.m (A. Rhines / K. Emanuel, https://texmex.mit.edu/pub/emanuel/soundings/).
% O getsounding.m original usa o endereço antigo do Wyoming (cgi-bin), que não existe mais,
% e lê colunas em posições fixas do formato antigo (vento SKNT em nós). Esta versão:
%   - usa o endereço atual: https://weather.uwyo.edu/wsgi/sounding?...&type=TEXT:LIST
%   - lê as colunas pela posição do cabeçalho (aceita campos vazios -> NaN)
%   - converte o vento SPED (m/s, formato atual) para nós (coluna 8 = SKNT, como no original)
%   - grava sounding.txt no formato lido pelo wyoming.f, header.txt e modsound.txt (p, T, UR 0-1)
%
% Uso:
%   [data, header, status, fonte] = getsounding_wyoming(83971, 1995, 12, 24, 12)
%   skewt(data(:,1), data(:,3), data(:,5)/100)
%
% Colunas de data: P (hPa), z (m), T (C), Td (C), UR (%), r (g/kg), DIR (graus),
%                  VEL (nós), THETA (K), THETA_E (K), THETA_V (K)
%
% Se o Wyoming não responder, tenta (nesta ordem) a cópia local sounding_AAAAMMDD_HHZ.txt
% e a cópia guardada no repositório da disciplina (só existe para os casos do exemplo).

if nargin < 6
    src = 'FM35';
end
station = num2str(station_id);
header = {'P (hPa)', 'z (m)', 'T (C)', 'DWPT (C)', 'RELH (%)', 'MIXR (g/kg)', ...
          'DRCT (deg)', 'SKNT (kts)', 'THTA (K)', 'THTE (K)', 'THTV (K)'};
data = NaN;
status = 0;

dstr = sprintf('%04d-%02d-%02d%%20%02d:00:00', year, month, day, hour);
url = sprintf('https://weather.uwyo.edu/wsgi/sounding?datetime=%s&id=%s&src=%s&type=TEXT:LIST', dstr, station, src);
arq_local = sprintf('sounding_%04d%02d%02d_%02dZ.txt', year, month, day, hour);
url_rep = ['https://raw.githubusercontent.com/reinaldohaas/tarefa-meso/master/metpack/' arq_local];

fontes = {url, arq_local, url_rep};
texto = '';
fonte = '';
for k = 1:numel(fontes)
    try
        if k == 2
            if exist(arq_local, 'file')
                texto = fileread(arq_local);
            end
        else
            texto = webread(fontes{k}, weboptions('Timeout', 60, 'ContentType', 'text'));
        end
    catch err
        fprintf('  falhou %s: %s\n', fontes{k}, err.message);
        texto = '';
    end
    if ~isempty(texto) && ~isempty(regexp(texto, 'PRES\s+HGHT', 'once'))
        fonte = fontes{k};
        break
    end
    texto = '';
end
if isempty(texto)
    fprintf('Erro: sondagem %s %04d-%02d-%02d %02dZ não encontrada.\n', station, year, month, day, hour);
    return
end
fprintf('Sondagem %s %04d-%02d-%02d %02dZ obtida de: %s\n', station, year, month, day, hour, fonte);

% Guarda a página baixada (cópia local para usar sem internet)
fid = fopen(arq_local, 'w');
fprintf(fid, '%s', texto);
fclose(fid);

% --- Leitura da tabela pelas posições do cabeçalho ---
linhas = regexp(regexprep(texto, '<[^>]*>', ''), '\r?\n', 'split');
i0 = find(~cellfun(@isempty, regexp(linhas, 'PRES\s+HGHT', 'once')), 1);
cab = linhas{i0};
nomes = regexp(cab, '\S+', 'match');
[~, fins] = regexp(cab, '\S+');
k = i0 + 1;
while k <= numel(linhas) && (isempty(strtrim(linhas{k})) || strncmp(strtrim(linhas{k}), '-', 1) || ~isempty(strfind(linhas{k}, 'hPa')))
    k = k + 1;
end
tab = [];
while k <= numel(linhas) && ~isempty(regexp(linhas{k}, '^\s*-?\d', 'once'))
    l = linhas{k};
    vals = NaN(1, numel(fins));
    ini = 1;
    for j = 1:numel(fins)
        fim = min(fins(j), length(l));
        if ini <= fim
            campo = strtrim(l(ini:fim));
            if ~isempty(campo)
                vals(j) = str2double(campo);
            end
        end
        ini = fins(j) + 1;
    end
    tab = [tab; vals]; %#ok<AGROW>
    k = k + 1;
end

col = @(nome) find(strcmp(nomes, nome), 1);
data = NaN(size(tab, 1), 11);
ordem = {'PRES', 'HGHT', 'TEMP', 'DWPT', 'RELH', 'MIXR', 'DRCT', 'SKNT', 'THTA', 'THTE', 'THTV'};
for j = 1:numel(ordem)
    c = col(ordem{j});
    if ~isempty(c)
        data(:, j) = tab(:, c);
    end
end
if isempty(col('SKNT')) && ~isempty(col('SPED'))
    data(:, 8) = tab(:, col('SPED')) * 1.943844;   % m/s -> nós
end
status = 1;

% --- Arquivos de entrada do wyoming.f ---
ok = all(isfinite(data(:, 1:4)), 2);
d = data(ok, :);
[~, iu] = unique(d(:, 1), 'stable');
d = d(iu, :);
[~, io] = sort(d(:, 1), 'descend');
d = d(io, :);

fid = fopen('sounding.txt', 'w');
fprintf(fid, '%s', repmat(sprintf('\n'), 1, 10));          % 10 linhas de cabeçalho (puladas pelo wyoming.f)
for r = 1:size(d, 1)
    fprintf(fid, '%7.1f%7.0f%7.1f%7.1f\n', d(r, 1), d(r, 2), d(r, 3), d(r, 4));
end
fprintf(fid, '</PRE>\n');
fprintf(fid, 'Station identifier: %s\n', station);
fprintf(fid, 'Station number: %s\n', station);
fprintf(fid, 'Observation time: %02d%02d%02d %02d00\n', mod(year, 100), month, day, hour);
fclose(fid);

fid = fopen('header.txt', 'w');
fprintf(fid, '%s %d %d %d %d', station, hour, month, day, year);
fclose(fid);

fid = fopen('modsound.txt', 'w');
for r = 1:size(d, 1)
    fprintf(fid, '%f %f %f\n', d(r, 1), d(r, 3), min(max(d(r, 5) / 100, 0), 1));
end
fclose(fid);
end
