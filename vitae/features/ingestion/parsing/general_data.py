from vitae.features.ingestion.adapters.schema import GeneralData

from . import _xml as xml

__all__ = ["general_data"]


def general_data(researcher_id: str, data: xml.Node) -> GeneralData:
    """Extract general data from the Lattes curriculum XML.

    This function navigates through the provided XML structure to extract
    general information about a researcher, such as their name, birthplace,
    ORCID ID, and professional institution details.

    Returns
    -------
    Researcher's general data.

    XML Schema
    ----------

        dados-gerais: {
            > nome-completo: string
            > nome-em-citacoes-bibliograficas: string
            nacionalidade: string
            > pais-de-nascimento: string
            > uf-nascimento: string
            > cidade-nascimento: string
            permissao-de-divulgacao: boolean
            data-falecimento: date
            sigla-pais-nacionalidade: string
            pais-de-nacionalidade: string
            > orcid-id: string

            resumo-cv: {
                > texto-resumo-cv-rh: string
            }

            outras-informacoes-relevantes: {
                outras-informacoes-relevantes: string
            }

            endereco: {
                flag-de-preferencia: string
                endereço-profissional: [
                    codigo-instituicao-empresa: string
                    > nome-instituicao-empresa: string
                    codigo-orgao: string
                    nome-orgao: string
                    codigo-unidade: string
                    nome-unidade: string
                    logradouro-complemento: string
                    pais: string
                    > uf: string
                    cep: string
                    > cidade: string
                    bairro: string
                    ddd: string
                    telefone: string
                    ramal: string
                    fax: string
                    caixa-postal: string
                    home-page: string
                ]
            }

            formacao-academica-titulacao: [...]
            atuacoes-profissionais: [...]
            areas-de-atuacao: [...]

            idiomas: [
                idioma: {
                    idioma: string
                    descricao-do-idioma: string
                    proeficiencia-de-leitura: string
                    proeficiencia-de-fala: string
                    proeficiencia-de-escrita: string
                    proeficiencia-de-compreensao: string
                }
            ]
        }

    """
    resume = data.first("resumo CV")

    return GeneralData(
        lattes_id=researcher_id,
        full_name=data["nome completo"] or "Invalid Name",
        quotes_names=data["nome em citacoes bibliograficas"],
        orcid=data["ORCID ID"],
        abstract=resume["texto resumo CV RH"],
    )
