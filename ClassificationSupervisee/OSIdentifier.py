# -*- coding: utf-8 -*-
"""
/*=========================================================================

Copyright (c) Centre National d'Etudes Spatiales
All rights reserved.

The "ClassificationSupervisee" Quantum GIS plugin is distributed
under the CeCILL licence version 2.
See Copyright/Licence_CeCILL_V2-en.txt or
http://www.cecill.info/licences/Licence_CeCILL_V2-en.txt for more details.


THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER AND CONTRIBUTORS ``AS IS''
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

=========================================================================*/
"""

import os
import sys

class OSIdentifier:

    @staticmethod
    def isWindows():
        return os.name =="nt"

    @staticmethod
    def isMac():
        return sys.platform == "darwin"
