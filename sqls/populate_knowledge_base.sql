-- Script para popular a tabela knowledge_base no Supabase - CLUBE NÁUTICO CAPIBARIBE
-- Execute este script no SQL Editor do Supabase

-- Limpar dados existentes (opcional)
-- DELETE FROM knowledge_base;

-- Inserir informações do Programa Sócio Mais Fiel do Nordeste - Náutico
INSERT INTO knowledge_base (title, content, category, tags, created_at, updated_at)
VALUES 

-- CATEGORIA CANCELAMENTO
(
    'Como cancelar minha adesão',
    'De acordo com o código de defesa do consumidor, você pode desistir e ter o valor integralmente devolvido em até 7 dias corridos a contar da data do pagamento, desde que não tenha utilizado o plano.',
    'cancelamento',
    ARRAY['cancelamento', 'desistir', 'adesão', 'devolução', 'código consumidor'],
    NOW(),
    NOW()
),
(
    'Como realizar cancelamento',
    'Para realizar o cancelamento do plano é necessário que o pagamento da mensalidade esteja em dia e se faz necessário o preenchimento do termo de cancelamento de associação que pode ser retirado na secretaria social do clube de maneira presencial ou solicitar de maneira online através do nosso whatsapp.',
    'cancelamento',
    ARRAY['cancelamento', 'termo', 'secretaria social', 'whatsapp', 'mensalidade em dia'],
    NOW(),
    NOW()
),

-- CATEGORIA CADASTRO FACIAL
(
    'Como cadastrar biometria facial',
    'O processo é bem simples, basta clicar no link https://captura.futebolcard.com/facial realizar o preenchimento dos dados de nome completo, data de nascimento, CPF e email, escolher um ambiente iluminado e sem muitos elementos de fundo para realizar a captura, clicar na câmera capturar a imagem, clicar em enviar e aguardar a confirmação em verde na tela que informa que a foto foi capturada com sucesso.',
    'cadastro_facial',
    ARRAY['biometria', 'facial', 'cadastro', 'captura', 'futebolcard'],
    NOW(),
    NOW()
),
(
    'Captura facial única',
    'Não, a captura é somente uma única vez e ficará valendo para todos os jogos.',
    'cadastro_facial',
    ARRAY['captura única', 'todos os jogos', 'biometria', 'facial'],
    NOW(),
    NOW()
),

-- CATEGORIA COMPRA DE INGRESSOS
(
    'Ingresso adicional na venda geral',
    'Sim, você pode comprar ingressos adicionais como não sócio, para isso, acesse o site da FutebolCard e compre seus ingressos, lembrando que não terá desconto do plano de sócio. A regra de acesso com o ingresso adicional é informada na confirmação da compra e se faz necessário que a pessoa que irá utilizar o ingresso adquirido tenha cadastrado a sua biometria facial.',
    'compra_ingressos',
    ARRAY['ingresso adicional', 'venda geral', 'futebolcard', 'sem desconto', 'biometria'],
    NOW(),
    NOW()
),
(
    'Como comprar ingressos não sendo sócio',
    'Para realização de compra de ingressos por pessoas que não são sócias, deve-se baixar o APP FutebolCard, realizar o cadastro, após criação de login e senha, deve-se escolher o jogo, logo em seguida escolher a quantidade de ingressos que serão adquiridos, depois disso é escolhido o setor onde o torcedor assistirá ao jogo. Após isso, cada ingresso deve ser preenchido com os dados pessoas de cada pessoa que irá utilizar o ingresso. Feito o cadastro confirma-se o valor do ingresso e segue para o pagamento. Aceita os termos e finaliza o processo.',
    'compra_ingressos',
    ARRAY['não sócio', 'app futebolcard', 'cadastro', 'jogo', 'setor'],
    NOW(),
    NOW()
),
(
    'Formas de pagamento ingressos',
    'As formas de pagamento disponíveis para compra de ingressos são Cartão de Crédito e Pix.',
    'compra_ingressos',
    ARRAY['pagamento', 'cartão crédito', 'pix', 'ingressos'],
    NOW(),
    NOW()
),
(
    'Bilheteria física requisitos',
    'Sim se faz necessário ter cadastro no app FutebolCard assim como estar com a facial já cadastrada.',
    'compra_ingressos',
    ARRAY['bilheteria física', 'app futebolcard', 'facial cadastrada', 'requisitos'],
    NOW(),
    NOW()
),
(
    'Sócio tem ingresso garantido',
    'A participação no Programa Sócio Mais Fiel do Nordeste não é a garantia da aquisição de ingresso, caso o ingresso não seja adquirido nas pré-vendas, seja via check-in ou compra de ingresso, de acordo com os descontos oferecidos por cada plano, o sócio mantém seus benefícios, mas concorre com todos os demais compradores habilitados para as fases seguintes de venda de ingressos.',
    'compra_ingressos',
    ARRAY['ingresso garantido', 'pré-venda', 'check-in', 'benefícios', 'venda geral'],
    NOW(),
    NOW()
),
(
    'Divulgação pré-vendas',
    'As datas e horários são sempre divulgadas através dos meios de comunicação oficiais (Site, Facebook, Twitter, Instagram..) do Clube e do Programa Sócio Mais Fiel do Nordeste.',
    'compra_ingressos',
    ARRAY['pré-venda', 'divulgação', 'comunicação oficial', 'redes sociais', 'datas'],
    NOW(),
    NOW()
),
(
    'Como funciona pré-venda',
    'A pré-venda se configura pelo início antecipado da venda de ingressos com exclusividade para os sócios Mais Fiel do Nordeste, após esse período, os ingressos remanecentes serão colocados à venda também para o público geral.',
    'compra_ingressos',
    ARRAY['pré-venda', 'exclusividade', 'sócios', 'público geral', 'antecipado'],
    NOW(),
    NOW()
),
(
    'Comprar depois da pré-venda',
    'Sim, a compra pode ser feita a qualquer momento até o intervalo da partida, de acordo com a disponibilidade de ingressos.',
    'compra_ingressos',
    ARRAY['após pré-venda', 'disponibilidade', 'intervalo partida', 'compra'],
    NOW(),
    NOW()
),
(
    'Quantos ingressos posso comprar',
    'Cada Sócio Mais Fiel do Nordeste ativo, titular ou dependente, tem direito a comprar um ingresso, conforme a disponibilidade. Exceto o sócio titular 100% Timba que possui o benefício de compra de mais 02 (dois) ingressos para seus convidados.',
    'compra_ingressos',
    ARRAY['quantidade ingressos', 'sócio ativo', 'titular', 'dependente', '100% timba', 'convidados'],
    NOW(),
    NOW()
),
(
    'Meia-entrada para sócios',
    'O regulamento do programa Sócio Mais Fiel do Nordeste prevê que só serão válidos os descontos previstos em seu plano. O ingresso de meia-entrada pode ser adquirido na venda geral, como torcedor comum, de acordo com as regras de meia-entrada.',
    'compra_ingressos',
    ARRAY['meia-entrada', 'descontos do plano', 'venda geral', 'torcedor comum'],
    NOW(),
    NOW()
),
(
    'Acesso ao ingresso após compra',
    'Seu ingresso estará carregado na sua biometria facial. Acesse as informações referentes a sua compra, através da sua Secretaria Virtual do Sócio Mais Fiel do Nordeste, na aba "Meus Pedidos".',
    'compra_ingressos',
    ARRAY['acesso ingresso', 'biometria facial', 'secretaria virtual', 'meus pedidos'],
    NOW(),
    NOW()
),

-- CATEGORIA PLANOS
(
    'Benefícios plano 100% Timba',
    'Prioridade na compra (mediante de check-in) de 02 ingressos com 100% de desconto nos setores: Hexa, Vermelho e Caldeirão do Aflitos; Inclusão de dependentes, cônjuge e filhos de até 18 anos, com valor mensal de R$24,90 por pessoa; O sócio titular recebe 03 camisas oficiais da linha masculina lançada na temporada (exceto goleiro e treino) em caso de antecipação das mensalidades na modalidade anual; O sócio titular pode votar nas eleições do Clube; Possibilidade de participação em promoções, ações e sorteios; Descontos exclusivos na Rede de Parceiros; Descontos em produtos nas lojas oficiais do Náutico.',
    'planos',
    ARRAY['100% timba', 'check-in', 'dependentes', 'camisas', 'eleições', 'descontos'],
    NOW(),
    NOW()
),
(
    'Benefícios plano Patrimonial',
    'Prioridade na aquisição de 01 ingresso com 70% de desconto nos setores Hexa, Vermelho e Caldeirão do Aflitos; Inclusão de dependentes, cônjuge e filhos de até 18 anos, com valor mensal de R$24,90 por pessoa; O sócio titular pode votar nas eleições do Clube; Possibilidade de participação em promoções, ações e sorteios; Descontos exclusivos na Rede de Parceiros; Descontos em produtos nas lojas oficiais do Náutico.',
    'planos',
    ARRAY['patrimonial', '70% desconto', 'dependentes', 'eleições', 'promoções'],
    NOW(),
    NOW()
),
(
    'Benefícios plano Vermelho de Luta',
    'Prioridade na aquisição de 01 ingresso com 70% de desconto nos setores Hexa, Vermelho e Caldeirão do Aflitos; Inclusão de dependentes, cônjuge e filhos de até 18 anos, com valor mensal de R$ 9,90 por pessoa; O sócio titular pode votar nas eleições do Clube; Possibilidade de participação em promoções, ações e sorteios; Descontos exclusivos na Rede de Parceiros; Descontos em produtos nas lojas oficiais do Náutico.',
    'planos',
    ARRAY['vermelho de luta', '70% desconto', 'dependentes R$9,90', 'eleições'],
    NOW(),
    NOW()
),
(
    'Benefícios plano Confraria',
    'Prioridade na aquisição de 01 ingresso com 100% de desconto nos jogos que o Náutico disputar em sua cidade; Possibilidade de participação em promoções, ações e sorteios; Descontos exclusivos na Rede de Parceiros; Descontos em produtos nas lojas oficiais do Náutico.',
    'planos',
    ARRAY['confraria', 'jogos na cidade', '100% desconto', 'promoções', 'rede parceiros'],
    NOW(),
    NOW()
),
(
    'Benefícios plano Branco de Paz',
    'Prioridade na compra (mediante de check-in) de 01 ingresso com 100% de desconto nos setores: Hexa, Vermelho e Caldeirão do Aflitos; Inclusão de dependentes, cônjuge e filhos de até 18 anos, com valor mensal de R$24,90 por pessoa; O sócio titular recebe 01 camisas oficial da linha masculina lançada na temporada (exceto goleiro e treino) em caso de antecipação das mensalidades na modalidade anual ; O sócio titular pode votar nas eleições do Clube; Possibilidade de participação em promoções, ações e sorteios; Descontos exclusivos na Rede de Parceiros; Descontos em produtos nas lojas oficiais do Náutico.',
    'planos',
    ARRAY['branco de paz', 'check-in', 'dependentes', '01 camisa', 'eleições'],
    NOW(),
    NOW()
),
(
    'Migração de planos descontinuados',
    'Após o fim do período adquirido, quando for realizar a renovação, caso seja de vontade do titular, o sócio pode escolher permanecer no plano que não é mais comercializado ou então migrar para um dos planos vigentes.',
    'planos',
    ARRAY['migração', 'planos descontinuados', 'renovação', 'planos vigentes'],
    NOW(),
    NOW()
),
(
    'Como trocar de plano',
    'A troca de plano pode ser feita na Secretaria Virtual para qualquer outro plano igual ou maior. Para alterar para um plano inferior, você deve entrar em contato com a Central de Atendimento do programa.',
    'planos',
    ARRAY['troca plano', 'secretaria virtual', 'plano superior', 'central atendimento'],
    NOW(),
    NOW()
),
(
    'Planos para quem mora fora de PE',
    'Sim, você pode escolher entre os planos Confraria ou Everybody is Náutico, de acordo com a localização em que mora.',
    'planos',
    ARRAY['fora pernambuco', 'confraria', 'everybody náutico', 'localização'],
    NOW(),
    NOW()
),
(
    'Valores dos planos',
    'Temos planos a partir de R$24,90 com diversos benefícios. Acesse e escolha seu plano.',
    'planos',
    ARRAY['valores', 'R$24,90', 'benefícios', 'escolher plano'],
    NOW(),
    NOW()
),
(
    'Plano Patrimonial - Jóia de 3 mil',
    'Caso o Clube Náutico de Capibaribe venha a terminar, os sócios que pagaram a Jóia Patrimonial no valor de R$ 3.000,00 terão participação no patrimônio financeiro do clube.',
    'planos',
    ARRAY['patrimonial', 'jóia 3 mil', 'patrimônio financeiro', 'participação'],
    NOW(),
    NOW()
),
(
    'Plano Sou Nação - requisitos',
    'Caso queira se associar, vá à Secretaria do Clube (das 9h às 18h) com todos os documentos necessários para inscrição em algum programa social ativo do Governo Federal. O plano tem mensalidade de apenas R$11,00 e concede gratuidade em ingressos dos jogos do Náutico no Aflitos, limitado em 500 ingressos.',
    'planos',
    ARRAY['sou nação', 'programa social', 'R$11,00', 'gratuidade', '500 ingressos'],
    NOW(),
    NOW()
),
(
    'Documentos para dependentes',
    'A inclusão de dependentes é exclusiva aos planos 100% Timba, Branco de Paz e Patrimonial observando as regras: Para inclusão do (s) dependente (s), o Sócio Torcedor titular deve comparecer à Sede de Atendimento do SÓCIO MAIS FIEL DO NORDESTE com os documentos comprobatórios de familiaridade originais, para que seja realizado o cadastro de seu (s) dependente (s). Os documentos aceitos são: RG* Certidão de Nascimento* Certidão de Casamento* Declaração de União Estável* Certidão de Tutela. Serão aceitos como dependentes cônjuge e filhos de até 18 anos.',
    'planos',
    ARRAY['dependentes', '100% timba', 'branco paz', 'patrimonial', 'documentos', 'cônjuge', 'filhos 18 anos'],
    NOW(),
    NOW()
),

-- CATEGORIA CARTEIRINHA
(
    'Carteirinha substituída por biometria',
    'Com a implantação da biometria facial, o acesso é exclusivo com a facial, não se faz mais necessário a utilização da carteirinha no acesso ao jogo.',
    'carteirinha',
    ARRAY['biometria facial', 'acesso exclusivo', 'carteirinha', 'jogo'],
    NOW(),
    NOW()
),
(
    'Não emprestar carteirinha',
    'A carteirinha de sócio é pessoal. Não é permitido emprestar, ceder, locar ou transferir para outra pessoa, independentemente do grau de parentesco, sob pena de ser retida e ter o cadastro temporariamente bloqueado pelo Programa Sócio Mais Fiel do Nordeste, ou ainda arcando com ônus financeiro.',
    'carteirinha',
    ARRAY['carteirinha pessoal', 'não emprestar', 'bloqueio cadastro', 'ônus financeiro'],
    NOW(),
    NOW()
),
(
    'Documentos além da carteirinha',
    'É obrigatório e indispensável, sempre que solicitado, a apresentação pelo sócio torcedor Sócio Mais Fiel do Nordeste a carteirinha e o RG original ou outro documento oficial original com foto. O não cumprimento desta exigência por parte do sócio torcedor, poderá implicar na não autorização de acesso do sócio torcedor a praça de desporto ou ainda aquisição de ingresso.',
    'carteirinha',
    ARRAY['documentos obrigatórios', 'rg original', 'foto', 'acesso negado'],
    NOW(),
    NOW()
),
(
    'Segunda via carteirinha',
    'Você pode solicitar através da Central de Atendimento, onde é emitida a taxa de segunda via pelo valor de R$25,00. Caso prefira receber em casa, há uma taxa de envio de R$25,00.',
    'carteirinha',
    ARRAY['segunda via', 'central atendimento', 'R$25,00', 'taxa envio'],
    NOW(),
    NOW()
),

-- CATEGORIA PAGAMENTOS
(
    'Boleto por email',
    'Avisos de faturas são enviados mensalmente por e-mail. O sócio encontra o boleto seguindo as orientações que estão no e-mail. Caso você não receba, é possível emitir através da Secretaria Virtual no site do Programa Sócio Mais Fiel do Nordeste. Também é possível ir à Sede de Atendimento do Programa, localizada no Clube Náutico de Capibaribe.',
    'pagamentos',
    ARRAY['boleto', 'email', 'secretaria virtual', 'sede atendimento'],
    NOW(),
    NOW()
),
(
    'Trocar forma de pagamento',
    'Basta acessar sua secretaria virtual, na aba meus dados, clicar em forma de pagamento e escolher a opção desejada de como quer realizar os pagamentos futuros do seu plano de sócio.',
    'pagamentos',
    ARRAY['trocar pagamento', 'secretaria virtual', 'meus dados', 'forma pagamento'],
    NOW(),
    NOW()
),

-- CATEGORIA BENEFÍCIOS GERAIS
(
    'Usar descontos rede parceiros',
    'Entre na Secretaria Virtual, clique na opção Rede de Parceiros e escolha a loja que deseja aproveitar o desconto. Confira os descontos no hotsite exclusivo da loja.',
    'beneficios_gerais',
    ARRAY['rede parceiros', 'secretaria virtual', 'descontos', 'hotsite loja'],
    NOW(),
    NOW()
),
(
    'Como fazer anistia',
    'Para cadastros com mais de 12 meses em aberto, é aberto ao sócio a possibilidade de uma reativação do plano, passando a ter data de associação a data em que realizar o pagamento da taxa de reativação + a mensalidade vigente. Este processo pode ser realizado pela secretaria virtual, escolhendo um novo plano e uma nova forma de pagamento ou pela central de atendimento.',
    'beneficios_gerais',
    ARRAY['anistia', '12 meses aberto', 'reativação', 'taxa reativação', 'mensalidade'],
    NOW(),
    NOW()
),

-- CATEGORIA DADOS CADASTRAIS
(
    'Atualizar dados cadastro',
    'Você pode atualizar os dados pela Secretaria Virtual, mas, se precisar alterar seu e-mail, deve entrar em contato com a Central de Atendimento.',
    'dados_cadastrais',
    ARRAY['atualizar dados', 'secretaria virtual', 'alterar email', 'central atendimento'],
    NOW(),
    NOW()
),

-- CATEGORIA ADESÃO
(
    'Como fazer adesão',
    'Escolha um plano, Preencha seus dados de cadastro, Escolha sua forma de pagamento, Confime seu pagamento. Para aderir aos planos Sou Nação e Pet, será necessário entrar em contato com a Central de Atendimento para a apresentação da documentação.',
    'adesao',
    ARRAY['adesão', 'escolher plano', 'dados cadastro', 'pagamento', 'sou nação', 'pet'],
    NOW(),
    NOW()
),
(
    'Retirar carteirinha após adesão',
    'Você pode retirar sua carteirinha em nossa Sede de Atendimento Sócio Mais Fiel do Nordeste depois de sua adesão pelo site, basta apresentar seu documento de identificação.',
    'adesao',
    ARRAY['retirar carteirinha', 'sede atendimento', 'documento identificação', 'adesão site'],
    NOW(),
    NOW()
),

-- CATEGORIA CONTATO
(
    'Central de atendimento contato',
    'Nosso atendimento é através do chat, e-mail, e presencial. Endereço: Avenida Rosa e Silva 1086, Aflitos, Recife - PE. Horário de atendimento: De segunda a sexta-feira das 09h às 18h aos sábados das 09h às 13h.',
    'contato',
    ARRAY['central atendimento', 'chat', 'email', 'presencial', 'rosa e silva', 'aflitos', 'horário'],
    NOW(),
    NOW()
),

-- CATEGORIA REGULARIZAÇÃO
(
    'Regularizar plano até 11 mensalidades',
    'Se você possuir até 11 mensalidades pendentes de pagamento, poderá realizar o pagamento através da Secretaria Virtual em Pagamentos > Selecionar faturas > Pagar > Escolher meio de pagamento.',
    'regularizacao',
    ARRAY['regularizar', '11 mensalidades', 'secretaria virtual', 'pagamentos', 'faturas'],
    NOW(),
    NOW()
),
(
    'Reativar plano mais de 12 mensalidades',
    'Se você possuir 12 ou mais mensalidades pendentes de pagamento, deverá entrar em contato com Central de Atendimento e solicitar a reativação do plano.',
    'regularizacao',
    ARRAY['reativar', '12 mensalidades', 'central atendimento', 'reativação plano'],
    NOW(),
    NOW()
),
(
    'Antecipar mensalidades',
    'O sócio em dia poderá antecipar mensalidades nas vigências mensal, semestral ou anual através da Secretaria Virtual em Pagamentos > antecipar mensalidades > selecionar vigência. ATENÇÃO: A antecipação de mensalidades não anula faturas anteriores pendentes de pagamento.',
    'regularizacao',
    ARRAY['antecipar mensalidades', 'sócio em dia', 'mensal', 'semestral', 'anual', 'não anula faturas'],
    NOW(),
    NOW()
);

-- Verificar se os dados foram inseridos
SELECT COUNT(*) as total_documentos FROM knowledge_base;
SELECT category, COUNT(*) as quantidade FROM knowledge_base GROUP BY category ORDER BY category;