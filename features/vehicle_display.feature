# language: fr
Fonctionnalité: Affichage des offres véhicules par site pays
  En tant que client visitant un site spécifique à un pays
  Je veux voir toutes les durées disponibles pour le véhicule qui m'intéresse
  Avec le prix le moins cher pour chaque combinaison durée/km
  En respectant la règle : un véhicule immatriculé à l'étranger ne peut
  être proposé que sur une durée maximale de 6 mois.

  # ─────────────────────────────────────────────────────────────────────────────
  # SCÉNARIOS PRINCIPAUX (exemple utilisateur : V1=BE occasion, V2=LU neuf)
  # ─────────────────────────────────────────────────────────────────────────────

  Contexte:
    Etant donné que la base de données contient les véhicules suivants :
      | id | catalogue | type     | immatriculation |
      | V1 | MODEL-X   | occasion | BE              |
      | V2 | MODEL-X   | neuf     | LU              |
    Et que la base de données contient les offres suivantes :
      | vehicule | duree_mois | km_mois | prix |
      | V1       | 6          | 1000    | 480  |
      | V1       | 12         | 1000    | 450  |
      | V1       | 18         | 1000    | 400  |
      | V2       | 6          | 1000    | 520  |
      | V2       | 12         | 1000    | 470  |
      | V2       | 18         | 1000    | 420  |

  Scénario: Client luxembourgeois — 6 mois au prix belge (moins cher), 12 et 18 mois au prix luxembourgeois (seul dispo)
    Etant donné que je suis sur le site LU
    Quand je consulte le catalogue de véhicules
    Alors je dois voir les offres suivantes :
      | duree_mois | km_mois | prix | immatriculation | type     |
      | 6          | 1000    | 480  | BE              | occasion |
      | 12         | 1000    | 470  | LU              | neuf     |
      | 18         | 1000    | 420  | LU              | neuf     |

  # ─────────────────────────────────────────────────────────────────────────────
  # RÈGLE : priorité avancée par disponibilité
  # ─────────────────────────────────────────────────────────────────────────────

  Scénario: Une disponibilité immédiate gagne toujours contre une disponibilité future même moins chère
    Etant donné que la base de données contient les véhicules suivants :
      | id      | catalogue | type     | immatriculation | disponible_le |
      | NOW-BE  | PRIO-1    | occasion | BE              | 2026-04-01    |
      | SOON-BE | PRIO-1    | neuf     | BE              | 2026-04-20    |
    Et que la base de données contient les offres suivantes :
      | vehicule | duree_mois | km_mois | prix |
      | NOW-BE   | 6          | 1000    | 700  |
      | SOON-BE  | 6          | 1000    | 500  |
    Etant donné que je suis sur le site BE
    Et que nous sommes le 2026-04-10
    Quand je consulte le catalogue de véhicules
    Alors je dois voir les offres suivantes :
      | duree_mois | km_mois | prix | immatriculation | type     |
      | 6          | 1000    | 700  | BE              | occasion |

  Scénario: Entre plusieurs véhicules immédiatement disponibles, le prix est prioritaire
    Etant donné que la base de données contient les véhicules suivants :
      | id       | catalogue | type     | immatriculation | disponible_le |
      | PRICE-BE | PRIO-2    | occasion | BE              | 2026-04-01    |
      | PRICE-FR | PRIO-2    | neuf     | FR              | 2026-04-05    |
    Et que la base de données contient les offres suivantes :
      | vehicule | duree_mois | km_mois | prix |
      | PRICE-BE | 6          | 1000    | 600  |
      | PRICE-FR | 6          | 1000    | 550  |
    Etant donné que je suis sur le site BE
    Et que nous sommes le 2026-04-10
    Quand je consulte le catalogue de véhicules
    Alors je dois voir les offres suivantes :
      | duree_mois | km_mois | prix | immatriculation | type |
      | 6          | 1000    | 550  | FR              | neuf |

  Scénario: En disponibilité immédiate à prix égal, la plaque du pays consulté gagne
    Etant donné que la base de données contient les véhicules suivants :
      | id       | catalogue | type     | immatriculation | disponible_le |
      | LOCAL-FR | PRIO-3    | occasion | FR              | 2026-04-01    |
      | LOCAL-BE | PRIO-3    | neuf     | BE              | 2026-04-08    |
    Et que la base de données contient les offres suivantes :
      | vehicule | duree_mois | km_mois | prix |
      | LOCAL-FR | 6          | 1000    | 500  |
      | LOCAL-BE | 6          | 1000    | 500  |
    Etant donné que je suis sur le site BE
    Et que nous sommes le 2026-04-10
    Quand je consulte le catalogue de véhicules
    Alors je dois voir les offres suivantes :
      | duree_mois | km_mois | prix | immatriculation | type |
      | 6          | 1000    | 500  | BE              | neuf |

  Scénario: En disponibilité immédiate à prix égal sans plaque locale, le plus ancien disponible gagne
    Etant donné que la base de données contient les véhicules suivants :
      | id      | catalogue | type     | immatriculation | disponible_le |
      | OLD-FR  | PRIO-4    | occasion | FR              | 2026-03-01    |
      | NEW-LU  | PRIO-4    | neuf     | LU              | 2026-04-01    |
    Et que la base de données contient les offres suivantes :
      | vehicule | duree_mois | km_mois | prix |
      | OLD-FR   | 6          | 1000    | 500  |
      | NEW-LU   | 6          | 1000    | 500  |
    Etant donné que je suis sur le site BE
    Et que nous sommes le 2026-04-10
    Quand je consulte le catalogue de véhicules
    Alors je dois voir les offres suivantes :
      | duree_mois | km_mois | prix | immatriculation | type     |
      | 6          | 1000    | 500  | FR              | occasion |

  Scénario: Sans disponibilité immédiate, deux véhicules sous un mois sont départagés par le prix
    Etant donné que la base de données contient les véhicules suivants :
      | id       | catalogue | type     | immatriculation | disponible_le |
      | SOON-BE  | PRIO-5    | occasion | BE              | 2026-05-20    |
      | SOON-FR  | PRIO-5    | neuf     | FR              | 2026-05-25    |
    Et que la base de données contient les offres suivantes :
      | vehicule | duree_mois | km_mois | prix |
      | SOON-BE  | 6          | 1000    | 700  |
      | SOON-FR  | 6          | 1000    | 500  |
    Etant donné que je suis sur le site BE
    Et que nous sommes le 2026-05-01
    Quand je consulte le catalogue de véhicules
    Alors je dois voir les offres suivantes :
      | duree_mois | km_mois | prix | immatriculation | type |
      | 6          | 1000    | 500  | FR              | neuf |

  Scénario: Sans disponibilité immédiate, un seul véhicule sous un mois gagne même si un plus tardif est moins cher
    Etant donné que la base de données contient les véhicules suivants :
      | id        | catalogue | type     | immatriculation | disponible_le |
      | FIRST-BE  | PRIO-6    | occasion | BE              | 2026-05-10    |
      | LATER-BE  | PRIO-6    | neuf     | BE              | 2026-06-15    |
    Et que la base de données contient les offres suivantes :
      | vehicule | duree_mois | km_mois | prix |
      | FIRST-BE | 6          | 1000    | 700  |
      | LATER-BE | 6          | 1000    | 400  |
    Etant donné que je suis sur le site BE
    Et que nous sommes le 2026-05-01
    Quand je consulte le catalogue de véhicules
    Alors je dois voir les offres suivantes :
      | duree_mois | km_mois | prix | immatriculation | type     |
      | 6          | 1000    | 700  | BE              | occasion |

  Scénario: Sans disponibilité immédiate ni véhicule sous un mois, le premier disponible gagne
    Etant donné que la base de données contient les véhicules suivants :
      | id       | catalogue | type     | immatriculation | disponible_le |
      | JUNE-BE  | PRIO-7    | occasion | BE              | 2026-06-10    |
      | JULY-BE  | PRIO-7    | neuf     | BE              | 2026-07-01    |
    Et que la base de données contient les offres suivantes :
      | vehicule | duree_mois | km_mois | prix |
      | JUNE-BE  | 6          | 1000    | 700  |
      | JULY-BE  | 6          | 1000    | 400  |
    Etant donné que je suis sur le site BE
    Et que nous sommes le 2026-05-01
    Quand je consulte le catalogue de véhicules
    Alors je dois voir les offres suivantes :
      | duree_mois | km_mois | prix | immatriculation | type     |
      | 6          | 1000    | 700  | BE              | occasion |

  Scénario: Une nouvelle combinaison mois/km apparaît quand un stock local entre dans les 3 mois
    Etant donné que la base de données contient les véhicules suivants :
      | id       | catalogue | type     | immatriculation | disponible_le |
      | CAP-FR   | PRIO-8    | occasion | FR              | 2026-04-01    |
      | CAP-BE   | PRIO-8    | neuf     | BE              | 2026-07-20    |
    Et que la base de données contient les offres suivantes :
      | vehicule | duree_mois | km_mois | prix |
      | CAP-FR   | 6          | 1000    | 550  |
      | CAP-FR   | 12         | 1000    | 450  |
      | CAP-BE   | 12         | 1000    | 650  |
    Etant donné que je suis sur le site BE
    Et que nous sommes le 2026-04-27
    Quand je consulte le catalogue de véhicules
    Alors je dois voir les offres suivantes :
      | duree_mois | km_mois | prix | immatriculation | type |
      | 6          | 1000    | 550  | FR              | occasion |
      | 12         | 1000    | 650  | BE              | neuf |

  Scénario: Client français — 6 mois uniquement au prix belge (véhicules étrangers limités à 6 mois)
    Etant donné que je suis sur le site FR
    Quand je consulte le catalogue de véhicules
    Alors je dois voir les offres suivantes :
      | duree_mois | km_mois | prix | immatriculation | type     |
      | 6          | 1000    | 480  | BE              | occasion |

  Scénario: Client belge — le 6 mois au prix belge le moins cher, puis les longues durées locales
    Etant donné que je suis sur le site BE
    Quand je consulte le catalogue de véhicules
    Alors je dois voir les offres suivantes :
      | duree_mois | km_mois | prix | immatriculation | type     |
      | 6          | 1000    | 480  | BE              | occasion |
      | 12         | 1000    | 450  | BE              | occasion |
      | 18         | 1000    | 400  | BE              | occasion |

  # ─────────────────────────────────────────────────────────────────────────────
  # RÈGLE : véhicule étranger limité à 6 mois
  # ─────────────────────────────────────────────────────────────────────────────

  Scénario: Un véhicule étranger ne peut jamais apparaître au-delà de 6 mois
    Etant donné que la base de données contient les véhicules suivants :
      | id | catalogue | type | immatriculation |
      | VX | TEST-1    | neuf | BE              |
    Et que la base de données contient les offres suivantes :
      | vehicule | duree_mois | km_mois | prix |
      | VX       | 6          | 1000    | 300  |
      | VX       | 12         | 1000    | 270  |
      | VX       | 18         | 1000    | 250  |
    Etant donné que je suis sur le site FR
    Quand je consulte le catalogue de véhicules
    Alors je dois voir les offres suivantes :
      | duree_mois | km_mois | prix | immatriculation | type |
      | 6          | 1000    | 300  | BE              | neuf |

  Scénario: Un véhicule local garde toutes ses durées sur son propre site
    Etant donné que la base de données contient les véhicules suivants :
      | id | catalogue | type | immatriculation |
      | VY | TEST-2    | neuf | LU              |
    Et que la base de données contient les offres suivantes :
      | vehicule | duree_mois | km_mois | prix |
      | VY       | 6          | 1000    | 400  |
      | VY       | 12         | 1000    | 360  |
    Etant donné que je suis sur le site LU
    Quand je consulte le catalogue de véhicules
    Alors je dois voir les offres suivantes :
      | duree_mois | km_mois | prix | immatriculation | type |
      | 6          | 1000    | 400  | LU              | neuf |
      | 12         | 1000    | 360  | LU              | neuf |

  # ─────────────────────────────────────────────────────────────────────────────
  # RÈGLE : même durée/km → on affiche le prix le moins cher
  # ─────────────────────────────────────────────────────────────────────────────

  Scénario: Deux véhicules en concurrence sur la même durée et km — on affiche le moins cher
    Etant donné que la base de données contient les véhicules suivants :
      | id | catalogue | type     | immatriculation |
      | VA | TEST-3    | occasion | BE              |
      | VB | TEST-3    | neuf     | BE              |
    Et que la base de données contient les offres suivantes :
      | vehicule | duree_mois | km_mois | prix |
      | VA       | 6          | 1000    | 500  |
      | VB       | 6          | 1000    | 480  |
      | VA       | 12         | 1000    | 450  |
      | VB       | 12         | 1000    | 460  |
    Etant donné que je suis sur le site BE
    Quand je consulte le catalogue de véhicules
    Alors je dois voir les offres suivantes :
      | duree_mois | km_mois | prix | immatriculation | type |
      | 6          | 1000    | 480  | BE              | neuf |
      | 12         | 1000    | 450  | BE              | occasion |

  # ─────────────────────────────────────────────────────────────────────────────
  # RÈGLE : plusieurs options de km/mois pour une même durée
  # ─────────────────────────────────────────────────────────────────────────────

  Scénario: Plusieurs km/mois disponibles pour une même durée — chaque combinaison est affichée
    Etant donné que la base de données contient les véhicules suivants :
      | id | catalogue | type | immatriculation |
      | VC | TEST-4    | neuf | LU              |
    Et que la base de données contient les offres suivantes :
      | vehicule | duree_mois | km_mois | prix |
      | VC       | 6          | 500     | 320  |
      | VC       | 6          | 1000    | 410  |
      | VC       | 6          | 1500    | 490  |
      | VC       | 12         | 500     | 290  |
      | VC       | 12         | 1000    | 370  |
    Etant donné que je suis sur le site LU
    Quand je consulte le catalogue de véhicules
    Alors je dois voir les offres suivantes :
      | duree_mois | km_mois | prix | immatriculation | type |
      | 6          | 500     | 320  | LU              | neuf |
      | 6          | 1000    | 410  | LU              | neuf |
      | 6          | 1500    | 490  | LU              | neuf |
      | 12         | 500     | 290  | LU              | neuf |
      | 12         | 1000    | 370  | LU              | neuf |

  # ─────────────────────────────────────────────────────────────────────────────
  # RÈGLE : même durée/km avec concurrence étrangère vs locale
  # ─────────────────────────────────────────────────────────────────────────────

  Scénario: Véhicule étranger moins cher au 6 mois — il l'emporte pour cette durée, le local prend le relais ensuite
    # VD (FR, étranger sur BE) : proposé à 450 € pour 6 mois seulement (cap étranger)
    # VE (BE, local)           : proposé à 480/430/400 € pour 6/12/18 mois
    # → 6 mois : VD gagne (450 < 480), 12 et 18 mois : seul VE est disponible
    Etant donné que la base de données contient les véhicules suivants :
      | id | catalogue | type     | immatriculation |
      | VD | TEST-5    | occasion | FR              |
      | VE | TEST-5    | neuf     | BE              |
    Et que la base de données contient les offres suivantes :
      | vehicule | duree_mois | km_mois | prix |
      | VD       | 6          | 1000    | 450  |
      | VD       | 12         | 1000    | 420  |
      | VE       | 6          | 1000    | 480  |
      | VE       | 12         | 1000    | 430  |
      | VE       | 18         | 1000    | 400  |
    Etant donné que je suis sur le site BE
    Quand je consulte le catalogue de véhicules
    Alors je dois voir les offres suivantes :
      | duree_mois | km_mois | prix | immatriculation | type     |
      | 6          | 1000    | 450  | FR              | occasion |
      | 12         | 1000    | 430  | BE              | neuf     |
      | 18         | 1000    | 400  | BE              | neuf     |

  Scénario: Un même véhicule peut agréger plusieurs stocks de pays différents
    Etant donné que la base de données contient les véhicules suivants :
      | id    | catalogue | type     | immatriculation |
      | VF-BE | MODEL-Y   | occasion | BE              |
      | VF-LU | MODEL-Y   | neuf     | LU              |
    Et que la base de données contient les offres suivantes :
      | vehicule | duree_mois | km_mois | prix |
      | VF-BE    | 6          | 1000    | 480  |
      | VF-BE    | 12         | 1000    | 450  |
      | VF-BE    | 18         | 1000    | 400  |
      | VF-LU    | 6          | 1000    | 480  |
      | VF-LU    | 12         | 1000    | 470  |
      | VF-LU    | 18         | 1000    | 420  |
    Etant donné que je suis sur le site LU
    Quand je consulte le catalogue de véhicules
    Alors je dois voir les offres suivantes :
      | duree_mois | km_mois | prix | immatriculation | type     |
      | 6          | 1000    | 480  | LU              | neuf     |
      | 12         | 1000    | 470  | LU              | neuf     |
      | 18         | 1000    | 420  | LU              | neuf     |

  Scénario: La date de disponibilité limite les stocks pris en compte aux 3 prochains mois
    Etant donné que la base de données contient les véhicules suivants :
      | id       | catalogue | type     | immatriculation | disponible_le |
      | DATE-BE  | DATE-X    | occasion | BE              | 2026-05-15    |
      | DATE-LU  | DATE-X    | neuf     | LU              | 2026-09-01    |
    Et que la base de données contient les offres suivantes :
      | vehicule | duree_mois | km_mois | prix |
      | DATE-BE  | 6          | 1000    | 500  |
      | DATE-BE  | 12         | 1000    | 460  |
      | DATE-LU  | 6          | 1000    | 450  |
      | DATE-LU  | 12         | 1000    | 430  |
    Etant donné que je suis sur le site LU
    Et que nous sommes le 2026-04-27
    Quand je consulte le catalogue de véhicules
    Alors je dois voir les offres suivantes :
      | duree_mois | km_mois | prix | immatriculation | type     |
      | 6          | 1000    | 500  | BE              | occasion |
