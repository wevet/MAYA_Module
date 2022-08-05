# -*- coding: utf-8 -*-

class DictionnaireOrdonne:

    def __init__(self, base=None, **donnees):
        if base is None:
            base = {}
        self._cles = []
        self._valeurs = []
        if type(base) not in (dict, DictionnaireOrdonne):
            raise TypeError('The expected type is Dict.')
        for cle in base:
            self[cle] = base[cle]
        for cle in donnees:
            self[cle] = donnees[cle]

    def __repr__(self):
        str_value = '{'
        premier_passage = True
        for cle, valeur in self.items():
            if not premier_passage:
                str_value += ', '
            else:
                premier_passage = False
            str_value += repr(cle) + ': ' + repr(valeur)
        str_value += '}'
        return str_value

    def __str__(self):
        return repr(self)

    def __len__(self):
        return len(self._cles)

    def __contains__(self, cle):
        return cle in self._cles

    def __getitem__(self, cle):
        if cle not in self._cles:
            raise KeyError(('The key {0} is not in the dictionary').format(cle))
        else:
            indice = self._cles.index(cle)
            return self._valeurs[indice]

    def __setitem__(self, cle, valeur):
        if cle in self._cles:
            indice = self._cles.index(cle)
            self._valeurs[indice] = valeur
        else:
            self._cles.append(cle)
            self._valeurs.append(valeur)

    def __delitem__(self, cle):
        if cle not in self._cles:
            raise KeyError(('The key {0} is not in the dictionary').format(cle))
        else:
            indice = self._cles.index(cle)
            del self._cles[indice]
            del self._valeurs[indice]

    def __iter__(self):
        return iter(self._cles)

    def __add__(self, auto_objet):
        if type(auto_objet) is not type(self):
            raise TypeError('cannot be connected {0} et {1}'.format(type(self), type(auto_objet)))
        else:
            nouveau = DictionnaireOrdonne()
            for cle, valeur in self.items():
                nouveau[cle] = valeur
            for cle, valeur in auto_objet.items():
                nouveau[cle] = valeur
            return nouveau

    def items(self):
        for i, cle in enumerate(self._cles):
            valeur = self._valeurs[i]
            yield (cle, valeur)

    def keys(self):
        return list(self._cles)

    def values(self):
        return list(self._valeurs)

    def reverse(self):
        cles = []
        valeurs = []
        for cle, valeur in self.items():
            cles.insert(0, cle)
            valeurs.insert(0, valeur)

        self._cles = cles
        self._valeurs = valeurs

    def sort(self):
        cles_triees = sorted(self._cles)
        valeurs = []
        for cle in cles_triees:
            valeur = self[cle]
            valeurs.append(valeur)

        self._cles = cles_triees
        self._valeurs = valeurs