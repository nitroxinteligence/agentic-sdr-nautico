-- Script SQL para popular a tabela knowledge_base com FAQ do Náutico
-- Execute este script no Supabase SQL Editor

-- Limpar dados existentes (opcional - descomente se quiser limpar antes)
-- DELETE FROM knowledge_base;

-- Inserir dados do FAQ completo do Náutico
INSERT INTO knowledge_base (question, answer, category, keywords, metadata) VALUES

-- ========== CATEGORIA: CANCELAMENTO ==========
('Desisti da minha adesão. Como posso cancelar?',
 'De acordo com o código de defesa do consumidor, você pode desistir e ter o valor integralmente devolvido em até 7 dias corridos a contar da data do pagamento, desde que não tenha utilizado o plano.',
 'Cancelamento',
 ARRAY['cancelar', 'desistir', 'adesão', 'devolver', 'valor'],
 '{"source": "faq_oficial", "priority": "alta"}'::jsonb),

('Como posso realizar meu cancelamento?',
 'Para realizar o cancelamento do plano é necessário que o pagamento da mensalidade esteja em dia e se faz necessário o preenchimento do termo de cancelamento de associação que pode ser retirado na secretaria social do clube de maneira presencial ou solicitar de maneira online através do nosso whatsapp.',
 'Cancelamento',
 ARRAY['cancelamento', 'termo', 'secretaria', 'whatsapp', 'associação'],
 '{"source": "faq_oficial", "priority": "alta"}'::jsonb),

-- ========== CATEGORIA: CADASTRO FACIAL ==========
('Como faço para cadastrar minha facial para acesso aos jogos?',
 'O processo é bem simples, basta clicar no link https://captura.futebolcard.com/facial realizar o preenchimento dos dados de nome completo, data de nascimento, CPF e email, escolher um ambiente iluminado e sem muitos elementos de fundo para realizar a captura, clicar na câmera capturar a imagem, clicar em enviar e aguardar a confirmação em verde na tela que informa que a foto foi capturada com sucesso.',
 'Cadastro Facial',
 ARRAY['facial', 'cadastro', 'biometria', 'captura', 'foto'],
 '{"source": "faq_oficial", "priority": "alta"}'::jsonb),

('É necessário realizar a captura de foto todas as vezes que for comprar ingressos?',
 'Não, a captura é somente uma única vez e ficará valendo para todos os jogos.',
 'Cadastro Facial',
 ARRAY['captura', 'foto', 'única', 'jogos', 'biometria'],
 '{"source": "faq_oficial", "priority": "média"}'::jsonb),

-- ========== CATEGORIA: COMPRA DE INGRESSOS ==========
('Adquiri meu ingresso na pré-venda, posso adquirir outro na venda geral?',
 'Sim, você pode comprar ingressos adicionais como não sócio, para isso, acesse o site da FutebolCard e compre seus ingressos, lembrando que não terá desconto do plano de sócio. A regra de acesso com o ingresso adicional é informada na confirmação da compra e se faz necessário que a pessoa que irá utilizar o ingresso adquirido tenha cadastrado a sua biometria facial.',
 'Compra de Ingressos',
 ARRAY['ingresso', 'pré-venda', 'venda geral', 'futebolcard', 'adicional'],
 '{"source": "faq_oficial", "priority": "média"}'::jsonb),

('Não sou sócio, como consigo realizar a compra de ingressos?',
 'Para realização de compra de ingressos por pessoas que não são sócias, deve-se baixar o APP FutebolCard, realizar o cadastro, após criação de login e senha, deve-se escolher o jogo, logo em seguida escolher a quantidade de ingressos que serão adquiridos, depois disso é escolhido o setor onde o torcedor assistirá ao jogo. Após isso, cada ingresso deve ser preenchido com os dados pessoas de cada pessoa que irá utilizar o ingresso. Feito o cadastro confirma-se o valor do ingresso e segue para o pagamento.',
 'Compra de Ingressos',
 ARRAY['não sócio', 'app', 'futebolcard', 'cadastro', 'compra'],
 '{"source": "faq_oficial", "priority": "alta"}'::jsonb),

('Em quais formas de pagamento consigo comprar meu ingresso?',
 'As formas de pagamento disponíveis para compra de ingressos são Cartão de Crédito e Pix.',
 'Compra de Ingressos',
 ARRAY['pagamento', 'cartão', 'crédito', 'pix', 'ingresso'],
 '{"source": "faq_oficial", "priority": "alta"}'::jsonb),

('Nas compras de bilheteria física ainda assim é necessário ter cadastro no App FutebolCard e Facial cadastrada?',
 'Sim se faz necessário ter cadastro no app FutebolCard assim como estar com a facial já cadastrada.',
 'Compra de Ingressos',
 ARRAY['bilheteria', 'física', 'app', 'facial', 'cadastro'],
 '{"source": "faq_oficial", "priority": "média"}'::jsonb),

('Sócio Mais Fiel do Nordeste tem ingresso garantido?',
 'A participação no Programa Sócio Mais Fiel do Nordeste não é a garantia da aquisição de ingresso, caso o ingresso não seja adquirido nas pré-vendas, seja via check-in ou compra de ingresso, de acordo com os descontos oferecidos por cada plano, o sócio mantém seus benefícios, mas concorre com todos os demais compradores habilitados para as fases seguintes de venda de ingressos.',
 'Compra de Ingressos',
 ARRAY['garantido', 'pré-venda', 'check-in', 'benefícios', 'fases'],
 '{"source": "faq_oficial", "priority": "alta"}'::jsonb),

('Quando as pré-vendas serão divulgadas?',
 'As datas e horários são sempre divulgadas através dos meios de comunicação oficiais (Site, Facebook, Twitter, Instagram..) do Clube e do Programa Sócio Mais Fiel do Nordeste.',
 'Compra de Ingressos',
 ARRAY['pré-venda', 'divulgação', 'datas', 'redes sociais', 'oficial'],
 '{"source": "faq_oficial", "priority": "média"}'::jsonb),

('Como funciona a pré-venda de ingressos para sócios?',
 'A pré-venda se configura pelo início antecipado da venda de ingressos com exclusividade para os sócios Mais Fiel do Nordeste, após esse período, os ingressos remanecentes serão colocados à venda também para o público geral.',
 'Compra de Ingressos',
 ARRAY['pré-venda', 'antecipado', 'exclusividade', 'remanescentes', 'público geral'],
 '{"source": "faq_oficial", "priority": "alta"}'::jsonb),

('Perdi a pré-venda, posso comprar depois?',
 'Sim, a compra pode ser feita a qualquer momento até o intervalo da partida, de acordo com a disponibilidade de ingressos.',
 'Compra de Ingressos',
 ARRAY['perdeu', 'pré-venda', 'intervalo', 'partida', 'disponibilidade'],
 '{"source": "faq_oficial", "priority": "média"}'::jsonb),

('Quantos ingressos posso comprar?',
 'Cada Sócio Mais Fiel do Nordeste ativo, titular ou dependente, tem direito a comprar um ingresso, conforme a disponibilidade. Exceto o sócio titular 100% Timba que possui o benefício de compra de mais 02 (dois) ingressos para seus convidados.',
 'Compra de Ingressos',
 ARRAY['quantidade', 'titular', 'dependente', '100% timba', 'convidados'],
 '{"source": "faq_oficial", "priority": "alta"}'::jsonb),

('Como funciona a compra de ingresso meia-entrada?',
 'O regulamento do programa Sócio Mais Fiel do Nordeste prevê que só serão válidos os descontos previstos em seu plano. O ingresso de meia-entrada pode ser adquirido na venda geral, como torcedor comum, de acordo com as regras de meia-entrada.',
 'Compra de Ingressos',
 ARRAY['meia-entrada', 'regulamento', 'desconto', 'venda geral', 'torcedor comum'],
 '{"source": "faq_oficial", "priority": "média"}'::jsonb),

('Feita a confirmação de compra, como posso ter acesso ao ingresso?',
 'Seu ingresso estará carregado na sua biometria facial. Acesse as informações referentes a sua compra, através da sua Secretaria Virtual do Sócio Mais Fiel do Nordeste, na aba "Meus Pedidos".',
 'Compra de Ingressos',
 ARRAY['confirmação', 'biometria', 'secretaria virtual', 'meus pedidos', 'acesso'],
 '{"source": "faq_oficial", "priority": "alta"}'::jsonb),

-- ========== CATEGORIA: PLANOS ==========
('Quais são os benefícios do plano 100% Timba?',
 'Prioridade na compra (mediante de check-in) de 02 ingressos com 100% de desconto nos setores: Hexa, Vermelho e Caldeirão do Aflitos; Inclusão de dependentes, cônjuge e filhos de até 18 anos, com valor mensal de R$24,90 por pessoa; O sócio titular recebe 03 camisas oficiais da linha masculina lançada na temporada (exceto goleiro e treino) em caso de antecipação das mensalidades na modalidade anual; O sócio titular pode votar nas eleições do Clube; Possibilidade de participação em promoções, ações e sorteios; Descontos exclusivos na Rede de Parceiros; Descontos em produtos nas lojas oficiais do Náutico.',
 'Planos',
 ARRAY['100% timba', 'check-in', 'dependentes', 'camisas', 'eleições'],
 '{"source": "faq_oficial", "priority": "alta"}'::jsonb),

('Quais são os benefícios do plano Patrimonial?',
 'Prioridade na aquisição de 01 ingresso com 70% de desconto nos setores Hexa, Vermelho e Caldeirão do Aflitos; Inclusão de dependentes, cônjuge e filhos de até 18 anos, com valor mensal de R$24,90 por pessoa; O sócio titular pode votar nas eleições do Clube; Possibilidade de participação em promoções, ações e sorteios; Descontos exclusivos na Rede de Parceiros; Descontos em produtos nas lojas oficiais do Náutico.',
 'Planos',
 ARRAY['patrimonial', '70% desconto', 'dependentes', 'eleições', 'parceiros'],
 '{"source": "faq_oficial", "priority": "alta"}'::jsonb),

('Quais são os benefícios do plano Vermelho de Luta?',
 'Prioridade na aquisição de 01 ingresso com 70% de desconto nos setores Hexa, Vermelho e Caldeirão do Aflitos; Inclusão de dependentes, cônjuge e filhos de até 18 anos, com valor mensal de R$ 9,90 por pessoa; O sócio titular pode votar nas eleições do Clube; Possibilidade de participação em promoções, ações e sorteios; Descontos exclusivos na Rede de Parceiros; Descontos em produtos nas lojas oficiais do Náutico.',
 'Planos',
 ARRAY['vermelho de luta', '70% desconto', 'dependentes', 'R$ 9,90', 'eleições'],
 '{"source": "faq_oficial", "priority": "alta"}'::jsonb),

('Quais são os benefícios do plano Confraria?',
 'Prioridade na aquisição de 01 ingresso com 100% de desconto nos jogos que o Náutico disputar em sua cidade; Possibilidade de participação em promoções, ações e sorteios; Descontos exclusivos na Rede de Parceiros; Descontos em produtos nas lojas oficiais do Náutico.',
 'Planos',
 ARRAY['confraria', '100% desconto', 'sua cidade', 'promoções', 'parceiros'],
 '{"source": "faq_oficial", "priority": "alta"}'::jsonb),

('Quais são os benefícios do plano Branco de Paz?',
 'Prioridade na compra (mediante de check-in) de 01 ingresso com 100% de desconto nos setores: Hexa, Vermelho e Caldeirão do Aflitos; Inclusão de dependentes, cônjuge e filhos de até 18 anos, com valor mensal de R$24,90 por pessoa; O sócio titular recebe 01 camisas oficial da linha masculina lançada na temporada (exceto goleiro e treino) em caso de antecipação das mensalidades na modalidade anual; O sócio titular pode votar nas eleições do Clube; Possibilidade de participação em promoções, ações e sorteios; Descontos exclusivos na Rede de Parceiros; Descontos em produtos nas lojas oficiais do Náutico.',
 'Planos',
 ARRAY['branco de paz', 'check-in', '100% desconto', 'camisa', 'eleições'],
 '{"source": "faq_oficial", "priority": "alta"}'::jsonb),

('Sou de um plano que não é mais comercializado, a migração de plano será automática para outro plano após o termino da vigência do meu pagamento?',
 'Após o fim do período adquirido, quando for realizar a renovação, caso seja de vontade do titular, o sócio pode escolher permanecer no plano que não é mais comercializado ou então migrar para um dos planos vigentes.',
 'Planos',
 ARRAY['plano descontinuado', 'migração', 'renovação', 'vigente', 'escolha'],
 '{"source": "faq_oficial", "priority": "média"}'::jsonb),

('Como faço a troca de plano?',
 'A troca de plano pode ser feita na Secretaria Virtual para qualquer outro plano igual ou maior. Para alterar para um plano inferior, você deve entrar em contato com a Central de Atendimento do programa.',
 'Planos',
 ARRAY['troca', 'secretaria virtual', 'plano maior', 'plano inferior', 'atendimento'],
 '{"source": "faq_oficial", "priority": "alta"}'::jsonb),

('Moro fora de Pernambuco, posso ser sócio?',
 'Sim, você pode escolher entre os planos Confraria ou Everybody is Náutico, de acordo com a localização em que mora.',
 'Planos',
 ARRAY['fora de pernambuco', 'confraria', 'everybody is náutico', 'localização'],
 '{"source": "faq_oficial", "priority": "média"}'::jsonb),

('Quais são os planos e valores do programa?',
 'Temos planos a partir de R$24,90 com diversos benefícios. Acesse e escolha seu plano.',
 'Planos',
 ARRAY['valores', 'R$24,90', 'benefícios', 'escolha', 'programa'],
 '{"source": "faq_oficial", "priority": "alta"}'::jsonb),

('O plano Patrimonial tem uma adesão de 3 mil e 25 reais. Por quê?',
 'Caso o Clube Náutico de Capibaribe venha a terminar, os sócios que pagaram a Jóia Patrimonial no valor de R$ 3.000,00 terão participação no patrimônio financeiro do clube.',
 'Planos',
 ARRAY['patrimonial', 'jóia', 'R$ 3.000', 'patrimônio', 'participação'],
 '{"source": "faq_oficial", "priority": "média"}'::jsonb),

('Quais são as regras para associar ao plano Sou Nação?',
 'Caso queira se associar, vá à Secretaria do Clube (das 9h às 18h) com todos os documentos necessários para inscrição em algum programa social ativo do Governo Federal. O plano tem mensalidade de apenas R$11,00 e concede gratuidade em ingressos dos jogos do Náutico no Aflitos, limitado em 500 ingressos.',
 'Planos',
 ARRAY['sou nação', 'programa social', 'R$11,00', 'gratuidade', '500 ingressos'],
 '{"source": "faq_oficial", "priority": "média"}'::jsonb),

('Quero trocar de plano, como fazer?',
 'Após login na secretaria virtual do site socio-nautico.futebolcard.com.br, na janela Meus Dados >Alterar Plano E escolhe para qual plano ir lembrando que a troca para planos de valor inferior ao que está cadastrado, só acontece mediante contato com o atendimento do Sócio Mais Fiel do Nordeste.',
 'Planos',
 ARRAY['trocar plano', 'secretaria virtual', 'alterar plano', 'valor inferior', 'atendimento'],
 '{"source": "faq_oficial", "priority": "alta"}'::jsonb),

('Quais são os documentos para incluir dependentes?',
 'A inclusão de dependentes é exclusiva aos planos 100% Timba, Branco de Paz e Patrimonial observando as regras: Para inclusão do (s) dependente (s), o Sócio Torcedor titular deve comparecer à Sede de Atendimento do SÓCIO MAIS FIEL DO NORDESTE com os documentos comprobatórios de familiaridade originais, para que seja realizado o cadastro de seu (s) dependente (s). Os documentos aceitos são: RG* Certidão de Nascimento* Certidão de Casamento* Declaração de União Estável* Certidão de Tutela. Serão aceitos como dependentes cônjuge e filhos de até 18 anos.',
 'Planos',
 ARRAY['dependentes', 'documentos', 'RG', 'certidão', 'cônjuge', 'filhos'],
 '{"source": "faq_oficial", "priority": "média"}'::jsonb),

-- ========== CATEGORIA: CARTEIRINHA ==========
('Já tenho carteirinha Sócio Mais Fiel do Nordeste. Posso ir ao estádio dos Aflitos para ver os jogos do Náutico?',
 'Com a implantação da biometria facial, o acesso é exclusivo com a facial, não se faz mais necessário a utilização da carteirinha no acesso ao jogo.',
 'Carteirinha',
 ARRAY['carteirinha', 'biometria facial', 'acesso', 'jogo', 'aflitos'],
 '{"source": "faq_oficial", "priority": "alta"}'::jsonb),

('Posso emprestar minha Carteira de Sócio Mais Fiel do Nordeste?',
 'A carteirinha de sócio é pessoal. Não é permitido emprestar, ceder, locar ou transferir para outra pessoa, independentemente do grau de parentesco, sob pena de ser retida e ter o cadastro temporariamente bloqueado pelo Programa Sócio Mais Fiel do Nordeste, ou ainda arcando com ônus financeiro.',
 'Carteirinha',
 ARRAY['emprestar', 'pessoal', 'ceder', 'bloqueado', 'ônus financeiro'],
 '{"source": "faq_oficial", "priority": "média"}'::jsonb),

('Além da carteirinha de sócio, preciso mostrar mais algum documento?',
 'É obrigatório e indispensável, sempre que solicitado, a apresentação pelo sócio torcedor Sócio Mais Fiel do Nordeste a carteirinha e o RG original ou outro documento oficial original com foto. O não cumprimento desta exigência por parte do sócio torcedor, poderá implicar na não autorização de acesso do sócio torcedor a praça de desporto ou ainda aquisição de ingresso.',
 'Carteirinha',
 ARRAY['documento', 'RG', 'oficial', 'foto', 'acesso', 'ingresso'],
 '{"source": "faq_oficial", "priority": "média"}'::jsonb),

('Como faço para pedir uma nova carteirinha de Sócio Mais Fiel do Nordeste?',
 'Você pode solicitar através da Central de Atendimento, onde é emitida a taxa de segunda via pelo valor de R$25,00. Caso prefira receber em casa, há uma taxa de envio de R$25,00.',
 'Carteirinha',
 ARRAY['segunda via', 'central atendimento', 'R$25,00', 'envio', 'casa'],
 '{"source": "faq_oficial", "priority": "média"}'::jsonb),

-- ========== CATEGORIA: PAGAMENTOS ==========
('Escolhi pagar com boleto. Vou receber por e-mail ou Correios?',
 'Avisos de faturas são enviados mensalmente por e-mail. O sócio encontra o boleto seguindo as orientações que estão no e-mail. Caso você não receba, é possível emitir através da Secretaria Virtual no site do Programa Sócio Mais Fiel do Nordeste. Também é possível ir à Sede de Atendimento do Programa, localizada no Clube Náutico de Capibaribe.',
 'Pagamentos',
 ARRAY['boleto', 'e-mail', 'faturas', 'secretaria virtual', 'sede'],
 '{"source": "faq_oficial", "priority": "alta"}'::jsonb),

('Como faço para trocar a minha forma de pagamento?',
 'Basta acessar sua secretaria virtual, na aba meus dados, clicar em forma de pagamento e escolher a opção desejada de como quer realizar os pagamentos futuros do seu plano de sócio.',
 'Pagamentos',
 ARRAY['trocar', 'forma pagamento', 'secretaria virtual', 'meus dados', 'opção'],
 '{"source": "faq_oficial", "priority": "alta"}'::jsonb),

-- ========== CATEGORIA: BENEFÍCIOS GERAIS ==========
('Como faço para usar os descontos da rede de parceiros?',
 'Entre na Secretaria Virtual, clique na opção Rede de Parceiros e escolha a loja que deseja aproveitar o desconto. Confira os descontos no hotsite exclusivo da loja.',
 'Benefícios Gerais',
 ARRAY['descontos', 'rede parceiros', 'secretaria virtual', 'loja', 'hotsite'],
 '{"source": "faq_oficial", "priority": "média"}'::jsonb),

('Como faço a anistia?',
 'Para cadastros com mais de 12 meses em aberto, é aberto ao sócio a possibilidade de uma reativação do plano, passando a ter data de associação a data em que realizar o pagamento da taxa de reativação + a mensalidade vigente. Este processo pode ser realizado pela secretaria virtual, escolhendo um novo plano e uma nova forma de pagamento ou pela central de atendimento.',
 'Benefícios Gerais',
 ARRAY['anistia', '12 meses', 'reativação', 'taxa', 'nova data'],
 '{"source": "faq_oficial", "priority": "média"}'::jsonb),

-- ========== CATEGORIA: DADOS CADASTRAIS ==========
('Como faço para atualizar meus dados de cadastro?',
 'Você pode atualizar os dados pela Secretaria Virtual, mas, se precisar alterar seu e-mail, deve entrar em contato com a Central de Atendimento.',
 'Dados Cadastrais',
 ARRAY['atualizar', 'dados', 'secretaria virtual', 'e-mail', 'central atendimento'],
 '{"source": "faq_oficial", "priority": "média"}'::jsonb),

-- ========== CATEGORIA: ADESÃO ==========
('Como faço minha adesão?',
 'Escolha um plano, Preencha seus dados de cadastro, Escolha sua forma de pagamento, Confirme seu pagamento. Para aderir aos planos Sou Nação e Pet, será necessário entrar em contato com a Central de Atendimento para a apresentação da documentação.',
 'Adesão',
 ARRAY['adesão', 'escolher plano', 'cadastro', 'pagamento', 'sou nação'],
 '{"source": "faq_oficial", "priority": "alta"}'::jsonb),

('Posso retirar a minha Carteira de Sócio?',
 'Você pode retirar sua carteirinha em nossa Sede de Atendimento Sócio Mais Fiel do Nordeste depois de sua adesão pelo site, basta apresentar seu documento de identificação.',
 'Adesão',
 ARRAY['retirar', 'carteira', 'sede atendimento', 'documento', 'identificação'],
 '{"source": "faq_oficial", "priority": "média"}'::jsonb),

-- ========== CATEGORIA: CONTATO ==========
('Onde fica a Central de atendimento e qual o contato de telefone?',
 'Nosso atendimento é através do chat, e-mail, e presencial. Endereço: Avenida Rosa e Silva 1086, Aflitos, Recife - PE. Horário de atendimento: De segunda a sexta-feira das 09h às 18h aos sábados das 09h às 13h.',
 'Contato',
 ARRAY['central atendimento', 'chat', 'e-mail', 'avenida rosa silva', 'horário'],
 '{"source": "faq_oficial", "priority": "alta"}'::jsonb),

-- ========== CATEGORIA: REGULARIZAÇÃO ==========
('Como faço para regularizar meu plano?',
 'Se você possuir até 11 mensalidades pendentes de pagamento, poderá realizar o pagamento através da Secretaria Virtual em Pagamentos > Selecionar faturas > Pagar > Escolher meio de pagamento.',
 'Regularização',
 ARRAY['regularizar', '11 mensalidades', 'secretaria virtual', 'faturas', 'meio pagamento'],
 '{"source": "faq_oficial", "priority": "alta"}'::jsonb),

('Como faço para reativar meu plano?',
 'Se você possuir 12 ou mais mensalidades pendentes de pagamento, deverá entrar em contato com Central de Atendimento e solicitar a reativação do plano.',
 'Regularização',
 ARRAY['reativar', '12 mensalidades', 'central atendimento', 'solicitar', 'reativação'],
 '{"source": "faq_oficial", "priority": "alta"}'::jsonb),

('Como faço para antecipar mensalidades?',
 'O sócio em dia poderá antecipar mensalidades nas vigências mensal, semestral ou anual através da Secretaria Virtual em Pagamentos > antecipar mensalidades > selecionar vigência. ATENÇÃO: A antecipação de mensalidades não anula faturas anteriores pendentes de pagamento.',
 'Regularização',
 ARRAY['antecipar', 'mensalidades', 'vigências', 'secretaria virtual', 'faturas pendentes'],
 '{"source": "faq_oficial", "priority": "média"}'::jsonb);

-- Verificar resultados da inserção
SELECT
    category,
    COUNT(*) as total_questions
FROM knowledge_base
GROUP BY category
ORDER BY total_questions DESC;

-- Mostrar algumas perguntas inseridas recentemente
SELECT
    question,
    category,
    array_length(keywords, 1) as num_keywords
FROM knowledge_base
WHERE metadata->>'source' = 'faq_oficial'
ORDER BY created_at DESC
LIMIT 10;