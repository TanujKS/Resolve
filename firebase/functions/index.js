const functions = require("firebase-functions");
const admin = require('firebase-admin');
const fetch = require("node-fetch")

admin.initializeApp();


exports.text = functions.https.onRequest(async (req, res) => {
  let congress = req.query.congress;
  let type = req.query.type;
  let number = req.query.number;

  const congress_data = admin.firestore().collection('congress_data').doc('bills').collection(type).doc(number);
  const doc = await congress_data.get();

  if (!doc.exists) {
  //  res.json({result: 'No such document!'}   );
    console.log(`${number} does not exist, saving now`)

    try {
      const response = await fetch(`https://api.congress.gov/v3/bill/${congress}/${type}/${number}/text?api_key=VQZwwZb2fRixhEk7g7o1dUscee2TcRIoqU8sc1HY`, {cache: 'no-cache'});

      if (response.ok) {
        const jsonResponse = await response.json()
        doc.set(jsonResponse)
        res.json(jsonResponse)
      }
    }
    catch(error) {
      res.json({error: error});
    }


  } else {
    console.log('Document data:', doc.data());
  }

  //res.json({result: doc.data().text})

});


exports.relevantBills = functions.https.onRequest(async (req, res) => {
  const limit = req.query.limit;
  const relevant_bills = admin.firestore().collection('relevant_bills');

  let bills = []
  for (let i = 0; i < limit; i++) {
    let doc = await relevant_bills.doc(i.toString()).get()
    bills.push(doc.data())
  }

  return res.json(bills)
});
