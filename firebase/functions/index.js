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
  let limit = req.query.limit;
  let offset = req.query.offset;

  if (offset == null) {
    offset = 0
  }

  if (limit == null) {
    limit = 20
  }

  if ((parseInt(limit) > 250) || (parseInt(limit) < 0)) {
    return res.json({"error": "Limit must be between 0 and 250"})
  }

  if ((parseInt(offset) > 250) || (parseInt(offset) < 0)) {
    return res.json({"error": "Offset must be between 0 and 250"})
  }

  const relevant_bills = admin.firestore().collection('relevant_bills')
  // const indexDoc = await relevant_bills.doc(offset).get()
  // let bills = await relevant_bills.startAfter(indexDoc).limit(parseInt(limit)).get()
  // bills.forEach(async (doc) => {
  //     const docData = doc.data();
  //     console.log(docData)
  //   });
  // return res.json(bills)
  let bills = []
  for (let i = parseInt(offset); i < parseInt(limit) + parseInt(offset); i++) {
    let doc = await relevant_bills.doc(i.toString()).get()
    data = doc.data()
    if (data != null) {
      bills.push(doc.data())
    }
  }

  return res.json({"count": bills.length, "bills": bills})

});


exports.updateStatus = functions.https.onRequest(async (req, res) => {
  let doc_ref = admin.firestore().collection("congress_data").doc("update_status")
  let doc = await doc_ref.get()
  let status = doc.get('updated')

  if (status == true) {
    doc_ref.set({'updated': false})
  }

  return res.json(status)
})
